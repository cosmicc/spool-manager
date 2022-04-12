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
verbose = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Spool:
    def __init__(self, spool_db, vars_file='/home/pi/klipper_config/saved_vars.cfg'):
        self.db = Path(spool_db)
        if not self.db.exists():
            self.con = sqlite3.connect(spool_db)
            self.con.row_factory = dict_factory
            self.cur = self.con.cursor()
            log.info(f'Spool database does not exist, creating')
            self.cur.execute("CREATE TABLE spools ('spool_id', 'material_type', 'color', 'manufacturer', 'density', 'diameter', 'tolerance', 'flow_rate', 'hotend_temp', 'bed_temp', 'chamber_temp', 'retract_length', 'retract_speed', 'pressure_advance', 'total_weight', 'spool_weight', 'remaining_weight', 'first_use', 'last_use', 'purchased_from', 'purchase_date', 'spool_cost', 'cost_per_gram');")
        else:
            log.debug(f'Existing database found {self.db}')
            self.con = sqlite3.connect(spool_db)
            self.con.row_factory = dict_factory
            self.cur = self.con.cursor()

        variables = configparser.ConfigParser()
        variables.read(vars_file)
        if 'Variables' not in variables:
            log.error('No section [Variables] in saved_vars.cfg, saving defaults')
            variables['Variables']['active_spool'] = "'None'"
            variables['Variables']['extra_weight'] = 0
            variables['Variables']['distance_to_extruder'] = 0
            variables['Variables']['calibration_offset'] = 0
            variables['Variables']['sensor_pin_out'] = 5
            variables['Variables']['sensor_pin_clk'] = 6
            variables.write(vars_file)
        else:
            if 'active_spool' not in variables['Variables']:
                variables['Variables']['active_spool'] = "'None'"
                variables.write(vars_file)
            if 'extra_weight' not in variables['Variables']:
                 variables['Variables']['extra_weight'] = 0
                 variables.write(vars_file)
            if 'distance_to_extruder' not in variables['Variables']:
                variables['Variables']['distance_to_extruder'] = 0
                variables.write(vars_file)
            if 'calibration_offset' not in variables['Variables']:
                 variables['Variables']['calibration_offset'] = 0
                 variables.write(vars_file)
            if 'sensor_pin_put' not in variables['Variables']:
                variables['Variables']['sensor_pin_out'] = 5
                variables.write(vars_file)
            if 'sensor_pin_clk' not in variables['Variables']:
                 variables['Variables']['sensor_pin_clk'] = 6
                 variables.write(vars_file)
            spool_id = variables['Variables']['active_spool'].replace("'", "")
            self.extra_weight = variables['Variables']['extra_weight']
            self.distance_to_extruder = variables['Variables']['distance_to_extruder']
            self.calibration_offset = variables['Variables']['calibration_offset']
            self.sensor_pin_out = variables['Variables']['sensor_pin_out']
            self.sensor_pin_clk = variables['Variables']['sensor_pin_clk']
            log.debug('Variables loaded from saved_vars.cfg')
            log.debug(f'Current Spool ID retrieved from saved_vars.cfg: {spool_id}')
            self.active_spool = self.get_spool(spool_id)
            if self.active_spool == 'None':
                log.error(f'Active spool ID [{spool_id}] does not exist in database')

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
        rows = len(self.get_all_data())
        log.info(f'Successfully imported {rows} spools from {csvfile} into database')

    def export_csv(self, csvfile):
        with open(csvfile, 'w', newline='') as f:
            writer = csv.writer(f)
            excon = sqlite3.connect(self.db)
            excur = excon.cursor()
            dataquery = excur.execute('SELECT * from spools')
            data = dataquery.fetchall()
            excon.close()
            writer.writerow(self.columns())
            writer.writerows(data)
        rows = len(self.get_all_data())
        log.info(f'Successfully exported {rows} spools to {csvfile}')

    def close(self):
        log.debug(f'Closing database {self.spool_db}')
        self.con.close()

    def get_all_data(self):
        dataquery = self.cur.execute("SELECT * FROM spools")
        data = dataquery.fetchall()
        return data

    def columns(self):
        data = self.cur.execute("SELECT * FROM spools")
        columns = []
        for column in data.description:
            columns.append(column[0])
        return columns

    def get_spool(self, spool_id):
        spoolquery = self.cur.execute(f"SELECT * FROM spools WHERE spool_id = '{spool_id}'")
        spooldata = self.cur.fetchall()
        if len(spooldata) > 0:
            log.debug(f'Found spool [{spool_id}]')
            return spooldata[0]
        else:
            log.debug(f'No spool found [{spool_id}]')
            return 'None'

    #def refresh_values(self):
    #    log.debug(f'Refreshing values for [{self.spool_id}]')
    #    self.current_weight_g = calculate_live_weight()
    #    self.loaded_spoolweight_g = self.loaded_spooldata['remaining _weight'].values[0] - self.loaded_spooldata['spool_weight'].values[0]
    #    self.loaded_spoolname = f"{self.loaded_spooldata['color'].values[0]} {self.loaded_spooldata['material'].values[0]} [{self.spool_id}]"
    #    self.loaded_spoollength_m = float(self.loaded_spooldata['ramaining_length'].values[0])
    #    self.loaded_density = self.loaded_spooldata['density'].values[0]
    #    self.loaded_total_weight = self.loaded_spooldata['total_weight'].values[0]
    #    self.loaded_total_volume = self.loaded_total_weight / self.loaded_density
    #    self.diameter_mm = float(self.loaded_spooldata['diameter'].values[0])

    def cross_area(self, spooldata):
        return (float(spooldata['diameter']))/2 ** 2 * 3.1415926535

    def total_volume(self, spooldata):
        return float(spooldata['total_weight']) / float(spooldata['density'])

    def remaining_volume(self, spooldata):
        return (float(spooldata['remaining_weight']) - float(spooldata['spool_weight'])) / float(spooldata['density'])

    def total_length(self, spooldata):
        return self.total_volume(spooldata) / self.cross_area(spooldata)

    def remaining_length(self, spooldata):
        return self.remaining_volume(spooldata) / self.cross_area(spooldata)

    def used_length(self, spooldata):
        return self.total_length(spooldata) - self.remaining_length(spooldata)

    def get_current_weight(self):
        pass

    def print_spool(self, spooldata):
        log.info(f'Loaded Spool: {spooldata["spool_id"]}')
        if verbose:
            log.info(f'Filament Diameter: {float(spooldata["diameter"]):.2f} mm')
            log.info(f'Filament Density: {spooldata["density"]} g/cm^3')
            log.debug(f'Filament Cross-Section Area: {self.cross_area(spooldata):.8f} mm')

            log.info(f'Spool Only Weight: {float(spooldata["spool_weight"]):.3f} g')
            log.info(f'Full Filament Weight: {float(spooldata["total_weight"]):.3f} g')
            log.debug(f'Full Filament Volume: {self.total_volume(spooldata):.3f} cm^3')
            log.info(f'Full Filament Length: {self.total_length(spooldata):.3f} m')

            log.debug(f'Remaining Filament Volume: {self.remaining_volume(spooldata):.3f} cm^3')

        log.info(f'Filament Purchased on {spooldata["purchase_date"]} from {spooldata["purchased_from"]}')
        log.info(f'Filament first used on {spooldata["first_use"]}')
        log.info(f'Filament Last used on {spooldata["last_use"]}')
        log.info(f'Filament Length Used: {self.used_length(spooldata):.3f} m')
        log.info(f'Remaining Weight: {float(spooldata["remaining_weight"]) - float(spooldata["spool_weight"]):.2f} g')
        log.info(f'Remaining Length: {self.remaining_length(spooldata):.3f} m')


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

