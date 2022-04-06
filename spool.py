#!/usr/bin/env python3.7

#
# Weighted Spool Manager for Klipper
#
# Utilizes the HX711 Load sensor to calculate and save filament data
#
# Written by Ian Perry ianperry99@gmail.com
# https://github.com/cosmicc/spool-manager
#

import sys
import pandas as pd
import configparser
import logging
import RPi.GPIO as GPIO
from hx711 import HX711
from wrapt_timeout_decorator import timeout


class Spool:
    def __init__(self, spool_id):
        self.spool_id = spool_id.upper()
        self.spooldata = pd.read_csv(spool_data)
        spool_count = len(self.spooldata.index)
        log.debug(f'Loaded {spool_count} spools')
        self.loaded_spooldata = self.spooldata.loc[self.spooldata['spool_code'] == self.spool_id.upper()]
        if len(self.loaded_spooldata.index) == 0:
            logger.error(f'Spool Code [{loaded_spoolcode}] not found in spool data')
            exit(2)
        log.debug(f'Found Spool Data for [{self.spool_id}]')
        self.refresh_values()
        self.calculate_values()

    def reload_data(self):
        self.spooldata = pd.read_csv(spool_data)
        self.loaded_spooldata = self.spooldata.loc[self.spooldata['spool_code'] == self.spool_id.upper()]
        log.debug(f'Data loaded for [{self.spool_id}]')
        self.refresh_values()
        self.calculate_values()

    def refresh_values(self):
        log.debug(f'Refreshing values for [{self.spool_id}]')
        self.current_weight_g = calculate_live_weight()
        self.loaded_spoolweight_g = self.loaded_spooldata['remaining _weight'].values[0] - self.loaded_spooldata['spool_weight'].values[0]
        self.loaded_spoolname = f"{self.loaded_spooldata['color'].values[0]} {self.loaded_spooldata['material'].values[0]} [{self.spool_id}]"
        self.loaded_spoollength_m = float(self.loaded_spooldata['ramaining_length'].values[0])
        self.loaded_density = self.loaded_spooldata['density'].values[0]
        self.loaded_total_weight = self.loaded_spooldata['total_weight'].values[0]
        self.loaded_total_volume = self.loaded_total_weight / self.loaded_density
        self.diameter_mm = float(self.loaded_spooldata['diameter'].values[0])

    def calculate_values(self):
        log.debug(f'Calculating values for [{self.spool_id}]')
        self.cross_area_mm = (self.diameter_mm/2) ** 2 * 3.1415926535
        self.loaded_total_length_m = self.loaded_total_volume / self.cross_area_mm
        self.weight_difference_g = self.loaded_spoolweight_g - self.current_weight_g
        self.current_volume = self.current_weight_g / self.loaded_density
        self.current_length_m = self.current_volume / self.cross_area_mm
        self.length_used_m = (self.loaded_total_length_m - self.current_length_m)
        self.length_difference_mm = (self.loaded_spoollength_m - self.current_length_m) * 1000

    def get_current_weight(self):
        pass

    def print_values(self):
        log.info(f'Loaded Spool: {self.loaded_spoolname}')
        if verbose:
            log.info(f'Filament Diameter: {self.diameter_mm:.2f} mm')
            log.info(f'Filament Density: {self.loaded_density} g/cm^3')
            log.info(f'Filament Cross-Section Area: {self.cross_area_mm:.8f} mm')

            log.info(f'Full Filament Weight: {self.loaded_total_weight:.3f} m')
            log.info(f'Full Filament Volume: {self.loaded_total_volume:.3f} cm^3')
            log.info(f'Full Filament Length: {self.loaded_total_length_m:.3f} m')

        log.info(f'Stored Remaining Weight: {self.loaded_spoolweight_g:.2f} g')
        log.info(f'Current Filament Weight: {self.current_weight_g:.3f} m')
        log.info(f'Current Weight Difference: {self.weight_difference_g:.3f} g')

        log.debug(f'Current Filament Volume: {self.current_volume:.3f} cm^3')
        log.info(f'Current Filament Length: {self.current_length_m:.3f} g')
        log.info(f'Current Length Difference: {self.length_difference_mm:.3f} mm')

        log.info(f'Total Length Used: {self.length_used_m:.3f} m')

@timeout(3)
def calculate_live_weight():
    #log.debug('Reading values from load sensor')
    #try:
    #    measures = hx711.get_raw_data(num_measures=10)
    #except:
    #    log.error('Error reading load values')
    #    GPIO.cleanup()
    #    exit(3)
    #return measures
    return 998

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


if __name__ == '__main__':
    vars_file = '/home/pi/klipper_config/saved_vars.cfg'
    spool_data = '/home/pi/klipper_config/spools.csv'
    sensor_out_pin = 17 # GPIO pin for the weight sensor output
    sensor_clk_pin = 22 # GPIO pin for the weight sensor clock
    loglevel = logging.INFO

    console_handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(
            handlers=[console_handler,],
         format='%(message)s',
         level=loglevel)
    log = logging.getLogger()

    #initialize_sensor()
    try:
        mode = sys.argv[1]
    except IndexError:
        log.error('Must specify a action')
        exit(1)
    try:
        param2 = sys.argv[2]
    except IndexError:
        param2 = None
    try:
        param3 = sys.argv[3]
    except IndexError:
       param3 = None

    if mode != 'query' and mode != 'load' and mode != 'endprint' and mode != 'startprint':
        log.error(f'Action "{mode}" is invalid')
        exit(1)

    if param2:
        if param2.upper() == 'V' or param3.upper() == "V":
            verbose = True
        else:
            verbose = False
    else:
        verbose =False

    variables = configparser.ConfigParser()
    variables.read(vars_file)
    if 'Variables' not in variables:
        logger.error('No section [Variables] in saved_vars.cfg')
        exit(1)
    elif 'loaded_spool' not in variables['Variables']:
        logger.error('No variable loaded_spool in section [Variables]')
        exit(1)

    loaded_spoolcode = variables['Variables']['loaded_spool'].replace("'", "")
    extra_weight = variables['Variables']['extra_weight']
    distance_to_extruder = variables['Variables']['distance_to_extruder']
    calibration_offset = variables['Variables']['calibration_offset']

    log.debug(f'Current Spool ID retrieved from saved_vars.cfg: {loaded_spoolcode}')
    spool = Spool(loaded_spoolcode)

    if mode == 'query':
        spool.print_values()
        exit(0)
    elif mode == 'load' or mode == 'endprint':
        pass
        # Update Weight
        # Update Length

