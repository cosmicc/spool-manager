# spool-manager
## Filament Spool Manager for Klipper
### Utilizes a Load Sensor and a HX711 load cell amplifier to calculate filament use and stores the data, these are required.
### Optional HTU21D/SHT21/SI7021/HDC1080 Temperature & Humidity Sensor to monitor filament environment.

This is very new *not-running-yet* alpha work-in-progress side project.<br />
I havent found any satisfactory spool management options for klipper, so im making this for myself.<br />
I came from OctoPrint with the Spool-Manager plugin. It's the only thing I miss after migrating from OctoPrint, but klipper is way too good for me to go back.
I'm trying to not make this too custom so others can potentially use it or expand on it.<br />
Currently, it just uses GCode commands to operate, and uses the printer console to display output. This may change if I figure out better ways to "plug-in" to Klipper. I'm new to klipper, so i'm still trying to figure all this out.

This script requires all spools be labeled with a unique "spool id".  I use a single letter and number for the id, and attach a label to each spool with this id.
I use P1 for PLA filament #1, G4 for PETG filament #4, etc.  But you can use whatever spool ID's you choose, as long as they are unique for each spool of filament.<br />

This script will display & store information about all of your filament spools, including color, type, manufacturer, first use, last use, date purchased, filament diameter, filament density, filament weights, filament length total, filament length remaining, filament spool price, filament price per gram, and some others.<br />
It will calculate filament length remaining based on weight after each print and filament change & display and save this infomation.<br />

A calibration script is included to calibrate and recalibrate the weight sensors<br />

### General Requirements:
     Analog Load Cell (5kg Preferred for best accuracy) https://tinyurl.com/2p9857vx
     HX711 Load cell amplifier (Comes with most load cells)
     (Optional) HTU21D/SHT21/SI7021/HDC1080 Temp Sensor 
     Raspberry Pi running klipper
     Python 3.8+

### Install:
     cd ~
     git clone https://github.com/cosmicc/spool-manager.git
     cd spool-manager
     ./install.sh

*Python Requirements:*<br />
```
    moonraker-api (installed from install.sh)
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
A HX711 load amplifier board needs to be wired directly to your klipper's raspberry pi.  3.3v Power, Ground, Output, and Clock<br />
The Output and Clock pins are configured in the saved_vars.cfg file or with WEIGHT_SENSOR_PINS GCode.<br />

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
     
Add to your print end & print cancel macro:<br />
     `RUN_SHELL_COMMAND CMD=spool PARAMS=printend`
 
 GCode commands:<br />
     `SPOOL_INFO  # Displays information about the currently loaded spool of filament`<br />
     `CALIBRATE_SENSOR  # Runs the sensors calibration script`
     
### Todo & Potential Features:
  - [ ] Move weight sensor pins to saved_vars.cfg
  - [ ] Add a way to add new spools/edit spool data manually (and/or with Gcodes possibly)
  - [ ] Query other spools infomation that arnt currently loaded
  - [ ] Display filament results after end of each print
  - [ ] Add gcode execute before calibration to shut off any lights, fans, motors, heat
  - [ ] Add gcode option to modify weight sensor pins
  - [ ] Add gcode option to modify calibration_weight option
  - [ ] Add gcode option to modify distance_to_extruder option
  - [ ] Add gcode option to modify extra_weight option
  - [ ] Possibly move to mysql lite or postgresql database instead of saved csv data
  - [ ] Will have to create a csv export option if moved to real database backend
