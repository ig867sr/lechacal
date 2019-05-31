# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

""" Module for Lechacal RPICT3T1 Module (3 CT, 1 Temp) """

import copy
import uuid
import logging

from foglamp.common import logger
from foglamp.plugins.common import utils
from foglamp.services.south import exceptions

import serial

__author__ = "Scott Robertson"
__copyright__ = "Copyright (c) Scott Robertson"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"


_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'Lechacal RPICT3T1 Module Plugin',
        'type': 'string',
        'default': 'lechacal_RPICT3T1',
        'readonly': 'true'
    },
    'assetName': {
        'description': 'Name of Asset',
        'type': 'string',
        'default': 'lechacal_RPTCT3T1',
        'order': '1'
    },
    'serial_port': {
        'description': 'The Serial port name assigned to the RPICT3T1',
        'type': 'string',
        'default': '/dev/ttyAMA0',
        'order': '2'
    },
    'baudrate': {
        'description': 'The BAUD Rate of the Serial Port assigned to the RPICT3T1',
        'type': 'integer',
        'default': '38400',
        'order': '3'
    }
}

_LOGGER = logger.setup(__name__, level = logging.INFO)


def plugin_info():
    """ Returns information about the plugin.
    Args:
    Returns:
        dict: plugin information
    Raises:
    """

    return {
        'name': 'RPICT3T1 plugin',
        'version': '1.0',
        'mode': 'poll',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config):
    """ Initialise the plugin.
    Args:
        config: JSON configuration document for the South plugin configuration category
                DEFAULT:
   Returns:
        data: JSON object to be used in future calls to the plugin
    Raises:
    """
    handle = copy.deepcopy(config)
    return handle


def plugin_poll(handle):
    """ Extracts data from the sensor and returns it in a JSON document as a Python dict.

    Available for poll mode only.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        returns a sensor reading in a JSON document, as a Python dict, if it is available
        None - If no reading is available
    Raises:
        DataRetrievalError
    """

    port = handle['serial_port']['value']
    baudrate = handle['baudrate']['value']
    ser = serial.Serial(port, baudrate)

    counter = 0
    x = ser.readline()
    # _LOGGER.info('RPICT3T1: {}', format(str(x)))
    values = x.split()

    if (len(values) == 5):
        Current1 = float(values[1].decode('UTF-8'))
        Current2 = float(values[2].decode('UTF-8'))
        Current3 = float(values[3].decode('UTF-8'))
        Temperature1 = float(values[4].decode('UTF-8'))
    else:
        _LOGGER.info('RPICT3T1: {}', format(str(len(values))))

    try:
        time_stamp = utils.local_timestamp()
        readings = {
            'Current1': Current1,
            'Current2': Current2,
            'Current3': Current3,
            'Temperature': Temperature1
        }
        data = {
                'asset':     handle['assetName']['value'],
                'timestamp': time_stamp,
                'key':       str(uuid.uuid4()),
                'readings':  readings
        }

    except (Exception, RuntimeError) as ex:
        _LOGGER.exception("RPICT3T1 exception: {}", format(str(ex)))
        raise exceptions.DataRetrievalError(ex)
    else:
        return data


def plugin_reconfigure(handle, new_config):
    """ Reconfigures the plugin, it should be called when the configuration of the plugin is changed during the
        operation of the device service.
        The new configuration category should be passed.

    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    Raises:
    """

    _LOGGER.info("Old config for RPICT3T1 plugin {} \n new config {}".format(handle, new_config))
    new_handle = copy.deepcopy(new_config)
    return new_handle


def plugin_shutdown(handle):
    """ Shutdowns the plugin doing required cleanup, to be called prior to the South plugin service being shut down.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
        plugin shutdown
    """

    _LOGGER.info('RPICT3T1 plugin shut down.')
