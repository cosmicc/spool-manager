# spool-manager
## Filament Spool Manager for Klipper
### Utilizes a Load Sensor, a HX711 load cell amplifier board, and arduino microcontroller to calculate filament use, these are required.
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

### General Requirements:
     - Analog Load Cell (2kg or 5kg Preferred for best accuracy)
     - HX711 Load cell amplifier.  Sparkfun makes a HX711 that has dual input voltages for non 5v gpio tolerant arduinos.
     - An arduino. If your ardunio is only 3.3v gpio tolerant, consider the dual voltage sparkfun hx711
     - (Optional) HTU21D/SHT21/SI7021/HDC1080 Temp Sensor.  If using a filament dryer to feed printer, or just to monitor the open air your spool is in.
     - Raspberry Pi setup and running klipper
     - Python 3.8+

### Install:
     cd ~
     git clone https://github.com/cosmicc/spool-manager.git
     cd spool-manager
     ./install.sh

*Python Requirements:*<br />
```
    moonraker-api (installed from install.sh)
```
  
### Klipper Configuration:
  *Uses klippers save_variables config option.  You only need to add the [save_variables] to your printer.cfg if it doesn't already exist*

  **Add to klipper's printer.cfg:**
  
     [include spoolmanager.cfg]
     
     [save_variables]
     filename: ~/klipper_config/saved_vars.cfg
     
  A [Variables] section will be added to your saved_vars.cfg file if it doesnt exist, and it will also add any missing variables that spool-manager requires.<br />

  ** Add to your existing klipper macros:**

Add to your existing "Filament Load" macro:
  `SM-LOAD`

Add to your existing "Filament Unload" macro:
  `SM-UNLOAD`

Add to your existing "Start Print" macro:
  `SM-PRINTSTART`

Add to your existing "End Print" and "Cancel Print" macros:
  `SM-PRINTEND`


### Sensor Configuration:
The HX711 load amplifier board and optional temp/humidity sensor needs to be wired to the ESP32<br />
The arduino will communicate to the Raspberry Pi running Klipper over USB<br />
The arduino sketch spoolmanager.ino is included and needs to be flashed to the arduino.
The pins used to connect the sensors to the arduino can be set at the top of the sketch before flashing.<br />More information can be found at the top of the spoolmanager.ino file.<br />

Uses the gcode_shell_command.py extras script.  This will be copied to klipper extras by the install.sh script, assuming your klipper install directory is ~/klipper<br />

### Usage:
All results are displayed through the printer console<br />

     `SPOOL_INFO  # Displays information about the currently loaded spool of filament`<br />
     `CALIBRATE_SCALE  # Runs the sensors calibration script`
     
### Todo & Potential Features:
  - [ ] Add a way to add new spools/edit spool data manually (and/or with Gcodes possibly)
  - [ ] Query other spool infomation that are not currently loaded
  - [ ] Display filament results after end of each print
  - [ ] Add gcode execute before calibration to shut off any lights, fans, motors, heat
  - [ ] Add gcode option to modify weight sensor pins
  - [ ] Add gcode option to modify calibration_weight option
  - [ ] Add gcode option to modify distance_to_extruder option
  - [ ] Add gcode option to modify extra_weight option
  - [ ] Add USB serial communication option so non wifi arduinos can used to communicate to the RPi (instead of over network)
  - [x] Move to mysql lite or postgresql database instead of saved csv data
  - [x] Will have to create a csv export option if moved to real database backend
