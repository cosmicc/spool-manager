#!/usr/bin/env python3

#
# Sensor calibration tool for klipper spool manager 
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

@timeout(3)
def get_current_weight():
    log.debug('Reading values from load sensor')
    try:
        measures = hx711.get_raw_data(num_measures=10)
    except:
        log.error('Error reading load values')
        GPIO.cleanup()
        exit(3)
    log.debug(f'Load value measured: {measures}')
    return measures

def calculate_current_weight():
    log.info('Pausing before calibration starts')
    sleep(3)
    log.debug('Calibrating sensor data')
    weight_list = []
    for i in range(10):
        nw = get_current_weight()
        weight_list.append(nw)
        log.debug(f'Load value measured: {nw}')
    mf = most_frequent(weight_list)
    log.debug(f'Most frequest value: {mf}')
    return mf

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
        log.critical('Error initializing the load sensor')
        GPIO.cleanup()
        exit(3)

def most_frequent(List):
    counter = 0
    num = List[0]
    for i in List:
        curr_frequency = List.count(i)
        if(curr_frequency> counter):
            counter = curr_frequency
            num = i
    return num

if __name__ == '__main__':
    vars_file = '/home/pi/klipper_config/saved_vars.cfg'
    sensor_out_pin = 17 # GPIO pin for the weight sensor output
    sensor_clk_pin = 22 # GPIO pin for the weight sensor clock

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
        log.error('No section [Variables] in saved_vars.cfg')
        exit(1)

    # Run gcode to shut off heaters, motors, lights for least noise

    calibration_weight = variables['Variables']['calibration_weight']
    log.info('Calibrating weight sensors...')
    log.info(f'Make sure a {calibration_weight}g weight is on the sensors with no spool')
    log.info('DO NOT TOUCH ANYTHING ON OR NEAR SENSORS')
    current_weight = calculate_current_weight()
    log.info('Calibration complete')
    print(' ')

    stored_calibration_offset = variables['Variables']['calibration_value']
    extra_weight = variables['Variables']['extra_weight']
    log.info(f'Current calibration offset: {calibration_value}')
    log.info(f'Current calibration weight used: {calibration_weight} g')
    log.info(f'Extra weight on scale: {extra_weight} g')

    current_weight_offset = (current_weight - extra_weight)
    log.debug(f'Current weight with extra weight offset: {current_weight_offset} g')
    new_offset = calibration_weight - calibration_weight
    log.info(f'New calculated calibration offset: {new_offset}')
    variables['Variables']['calibration_value'] = new_offset

    with open(vars_file, 'w') as configfile:
        variables.write(configfile)

    log.info('Saved new calibration offset')
