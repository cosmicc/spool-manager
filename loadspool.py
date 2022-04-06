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

vars_file = '/home/pi/klipper_config/saved_vars.cfg'
spool_data = '/home/pi/klipper_config/spools.csv'
sensor_out_pin = 17 # GPIO pin for the weight sensor output
sensor_clk_pin = 22 # GPIO pin for the weight sensor clock
loglevel = logging.DEBUG

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
        level=loglevel)
log = logging.getLogger()

#initialize_sensor()
variables = configparser.ConfigParser()
variables.read(vars_file)
if 'Variables' not in variables:
    logger.error('No section [Variables] in saved_vars.cfg')
    exit(1)
elif 'loaded_spool' not in variables['Variables']:
    logger.error('No variable loaded_spool in section [Variables]')
    exit(1)
loaded_spoolcode = variables['Variables']['loaded_spool'].replace("'", "")
offset_weight = variables['Variables']['offset_weight']
log.debug(f'Current Spool ID read from saved_vars.cfg: {loaded_spoolcode}')

spooldata = pd.read_csv(spool_data)

spool_count = len(spooldata.index)
log.debug(f'Loaded {spool_count} spools')

loaded_spooldata = spooldata.loc[spooldata['spool_code'] == loaded_spoolcode.upper()]

if len(loaded_spooldata.index) == 0:
    logger.error(f'Spool Code [{loaded_spoolcode}] not found in spool data')
    exit(2)

log.debug(f'Found Spool Data for [{loaded_spoolcode}]')

loaded_spoolweight_g = loaded_spooldata['remaining _weight'].values[0] - loaded_spooldata['spool_weight'].values[0]
loaded_spoolname = f"{loaded_spooldata['color'].values[0]} {loaded_spooldata['material'].values[0]} [{loaded_spoolcode.upper()}]"
loaded_spoollength_mm = int(loaded_spooldata['ramaining_length'].values[0])

log.info(f'Loaded Spool: {loaded_spoolname}')
log.info(f'Remaining Weight: {loaded_spoolweight_g:.2f}g')

#live_weight = calculate_live_weight()
#weight_difference = loaded_spoolweight - live_weight
#log.info(f'Live Weight Difference: {weight_difference}g')

#log.debug(f'Resetting filament weight')
loaded_density = loaded_spooldata['density'].values[0]
loaded_total_weight = loaded_spooldata['total_weight'].values[0]
loaded_total_volume = loaded_total_weight / loaded_density
diameter_mm = float(loaded_spooldata['diameter'].values[0])
cross_area_mm = (diameter_mm/2) ** 2 * 3.1415926535
loaded_total_length_m = loaded_total_volume / cross_area_mm

log.debug(f"Filament density: {density}")
log.debug(f"Total Filament Weight: {loaded_total_weight")
log.debug(f'Total filament volume: {loaded_total_volume}')
#live_volume = loaded_spooldata['density'].values[0] / live_weight
log.debug(f'Filament diameter: {diameter_mm:.3f}mm')
log.debug(f'Filament cross section area: {cross_area_mm:.8f}mm')
log.info(f'Total Length: {loaded_total_length_m:.3f}m')


