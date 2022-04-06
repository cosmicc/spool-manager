#!/usr/bin/env python3.7

#
# Weighted Spool Manager for Klipper
#
# Written by Ian Perry ianperry99@gmail.com
# https://github.com/cosmicc/spool-manager
#

import pandas as pd
import configparser
import logging

vars_file = '/home/pi/klipper_config/saved_vars.cfg'
spool_data = '/home/pi/klipper_config/spools.csv'

Log_Format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename = "spoolmanager.log", filemode = "w", format = Log_Format, level = logging.INFO)
logger = logging.getLogger()

variables = configparser.ConfigParser()
variables.read(vars_file)
if 'Variables' not in variables:
    logger.error('No section [Variables] in saved_vars.cfg')
    exit(1)
elif 'loaded_spool' not in variables['Variables']:
    logger.error('No variable loaded_spool in section [Variables]')
    exit(1)
loaded_spoolcode = variables['Variables']['loaded_spool'].replace("'", "")
logger.info(f'Current Spool ID read from saved_vars.cfg: {loaded_spoolcode}')

spooldata = pd.read_csv(spool_data)

spool_count = len(spooldata.index)
logger.info(f'Loaded {spool_count} spools')


loaded_spooldata = spooldata.loc[spooldata['Spool Code'] == loaded_spoolcode.upper()]

if len(loaded_spooldata.index) == 0:
    logger.error(f'Spool Code [{loaded_spoolcode}] not found in spool data')
    exit(2)

logger.info(f'Found Spool Data for [{loaded_spoolcode}]')
