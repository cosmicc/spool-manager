#!/usr/bin/env python3

#
# Spool Manager for Klipper
#
# Utilizes a load sensor and HX711 load sensor amplifier to calculate and save filament data
#
# Written by Ian Perry ianperry99@gmail.com
# https://github.com/cosmicc/spool-manager
#

import sys
import sqlite3
import configparser
import logging
import csv
import RPi.GPIO as GPIO
from pathlib import Path
from hx711 import HX711
from wrapt_timeout_decorator import timeout

log = logging.getLogger()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Spool:
    def __init__(self, spool_db):
        self.db = Path(spool_db)
        if not self.db.exists():
            self.con = sqlite3.connect(spool_db)
            self.cur = self.con.cursor()
            log.info(f'Spool database does not exist, creating')
            self.cur.execute("CREATE TABLE spools ('spool_id', 'material_type', 'color', 'manufacturer', 'density', 'diameter', 'total_volume', 'remaining_volume', 'tolerance', 'flow_rate', 'hotend_temp', 'bed_temp', 'chamber_temp', 'retract_length', 'retract_speed', 'pressure_advance', 'total_weight', 'spool_weight', 'used_weight', 'remaining_weight', 'total_length', 'used_length', 'remaining_length', 'first_use', 'last_use', 'purchased_from', 'purchase_date', 'spool_cost', 'cost_per_gram');")
        else:
            log.debug(f'Existing database found {self.db}')
            self.con = sqlite3.connect(spool_db)
            self.con.row_factory = dict_factory
            self.cur = self.con.cursor()

    def import_csv(self, csvfile):
        with open (csvfile, 'r') as f:
            reader = csv.reader(f)
            data = next(reader)
            query = 'insert into spools values ({0})'
            query = query.format(','.join('?' * len(data)))
            self.cur.execute(query, data)
            for data in reader:
                self.cur.execute(query, data)
            self.con.commit()

    def close(self):
        log.debug(f'Closing database {self.spool_db}')
        self.con.close()

    def list_data(self):
        dataquery = self.cur.execute("SELECT * FROM spools")
        data = dataquery.fetchall()
        return data

    def columns(self):
        data = self.cur.execute("SELECT * FROM spools")
        for column in data.description:
            print(column[0])

    def query_spool(self):
        self.spooldata = 1
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
    spool_db = '/home/pi/klipper_config/spools.db'
    vars_file = '/home/pi/klipper_config/saved_vars.cfg'
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
        log.error('No section [Variables] in saved_vars.cfg')
        exit(1)
    elif 'loaded_spool' not in variables['Variables']:
        log.error('No variable loaded_spool in section [Variables]')
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

