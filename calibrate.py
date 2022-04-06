#!/usr/bin/env python3.7

#
# Sensor calibration tool for the spool manager 
#
# Written by Ian Perry ianperry99@gmail.com
# https://github.com/cosmicc/spool-manager
#

import sys
import configparser
import logging
import RPi.GPIO as GPIO
from hx711 import HX711
from wrapt_timeout_decorator import timeout

vars_file = '/home/pi/klipper_config/saved_vars.cfg'
sensor_out_pin = 17 # GPIO pin for the weight sensor output
sensor_clk_pin = 22 # GPIO pin for the weight sensor clock

@timeout(3)
def calculate_live_weight():
    log.debug('Reading values from load sensor')
    try:
        measures = hx711.get_raw_data(num_measures=10)
    except:
        log.error('Error reading load values')
        GPIO.cleanup()
        exit(3)
    return measures

@timeout(3)
def initialize_sensor():
    log.debug('Initalizing load sensor')
    try:
        hx711 = HX711(
            dout_pin=sensor_out_pin,
            pd_sck_pin=sensor_clk_pin,
            channel='A',
            gain=64
        )

        hx711.reset()   # Before we start, reset the HX711 (not obligate)
    except:
        log.error('Error initializing the load sensor')
        GPIO.cleanup()
        exit(3)

console_handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(
        handlers=[console_handler,],
        format='%(message)s',
        level=logging.INFO)
log = logging.getLogger()

initialize_sensor()
variables = configparser.ConfigParser()
variables.read(vars_file)
if 'Variables' not in variables:
    logger.error('No section [Variables] in saved_vars.cfg')
    exit(1)
calibration_value = variables['Variables']['calibration_value']
calibration_weight = variables['Variables']['calibration_weight']
log.debug(f'Current calibration value: {calibration_value}')
log.info(f'
