# spool-manager
## Weighted Spool Manager for Klipper
### Utilizes the HX711 Load sensor to calculate filament use and stores the data, this is required.

This is very new alpha WIP side project.
AFAIK there isn't any good spool management options for klipper, so im making this for myself.
I'm trying to not make it too custom so others can potentially use it/expand on it.

This script requires all spools be labeled with a unique "spool id".  I use a single letter and number for the id, and affix a label each spool with this id.
I use P1 for PLA filament #1, G4 for PETG filament #4, etc.  But you can use whatever spool ID's you choose, as long as they are unique for each spool of filament.

### General Requirements:
     Raspberry Pi running klipper
     Python 3.7+

### Install:
     cd ~
     git clone https://github.com/cosmicc/spool-manager.git
     cd spool-manager
     ./install.sh

*Python Requirements:*<br />
```
    pandas (installed from install.sh)
    hx711 (installed from install.sh)
```
  
### Klipper Configuration:
  *Uses klippers save_variables config option*

  **Add to klipper's printer.cfg:**
  
     [save_variables]
     filename: ~/klipper_config/saved_vars.cfg
  
     [gcode_shell_command spool]
     command: ~/spool-manager/spool.py
     timeout: 10
     verbose: True

     [gcode_shell_command calibrate_weight]
     command: ~/spool-manager/calibrate.py
     timeout: 30
     verbose: True

  **Add to klipper's printer.cfg (or wherever you put your klipper gcode macros)**<br />
     `to be added`

  **Other klipper gcode examples:**<br />
     `to be added`
     
  After A [Variables] section will be added to your saved.vars.cfg file if it doesnt exist, and it will also add any missing variables
     
### Sensor Configuration:
A HX711 sensor board needs to be wired directly to your klipper's raspberry pi.  3.3v Power, Ground, Output, and Clock<br />
1, 2 or 4 sensors can be wired to 1 HX711 board, depending on the footprint of your spool mount, filament dryer, etc, you may want to use multiple sensors.  The HX711 board will deliver them all as 1 weight reading to the raspberry pi.  See specific sensor wiring options for your HX711 board so the number of sensors you use are wired to the board correctly.<br />

The Output and Clock pins are configured in the saved_vars.cfg file or with WEIGHT_SENSOR_PINS GCode.

Uses gcode_shell_command.py extras script.  This we be copied to klipper extras from the install.sh script, assuming your klipper install is a ~/klipper<br />

### Usage:
All results are displayed through the printer console

*GCode Commands add to your existing macros:*<br />
Add to your filament load macro:<br />
     `{% set SPOOL_ID = params.SPOOL_ID %}`<br />
     `SAVE_VARIABLE VARIABLE=loaded_spool VALUE='"{SPOOL_ID}"'`<br />
     `RUN_SHELL_COMMAND CMD=spool PARAMS=load`
     
Add to your filament unload macro:<br />
     `RUN_SHELL_COMMAND CMD=spool PARAMS=unload`
     
Add to your print start macro:<br />
     `RUN_SHELL_COMMAND CMD=spool PARAMS=printstart` 
     
Add to your print end macro:<br />
     `RUN_SHELL_COMMAND CMD=spool PARAMS=printend`
 
 GCode commands:<br />
     `SPOOL_INFO  # Displays information about the currently loaded spool of filament`<br />
     `CALIBRATE_SENSOR  # Runs the sensors calibration script`
     
### Todo & Potential Features:
  - [ ] Move weight sensor pins to saved_vars.cfg
  - [ ] Add a way to add new spools/edit spool data manually (and/or with Gcodes possibly)
  - [ ] Add gcode execute before calibration to shut off any lights, fans, motors, heat
  - [ ] Add gcode option to modify weight sensor pins
  - [ ] Add gcode option to modify calibration_weight option
  - [ ] Add gcode option to modify distance_to_extruder option
  - [ ] Add gcode option to modify extra_weight option
  - [ ] Possibly move to mysql lite or postgresql database instead of saved csv data
  - [ ] Will have to create a csv export option if moved to real database backend
