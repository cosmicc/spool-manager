# spool-manager
## Weighted Spool Manager for Klipper
### Utilizes the HX711 Load sensor to calculate filament use and stores the data.

This is very new alpha WIP side project.
AFAIK there isn't any good spool management options for klipper, so im making this for myself.
I'm trying to not make it too custom so others can potentially use it/expand on it.

This script requires all spools be labeled with a unique "spool id".  I use a single letter and number for the id, and affix a label each spool with this id.
I use P1 for PLA filament #1, G4 for PETG filament #4, etc.  But you can use whatever spool ID's you choose, as long as they are unique for each spool of filament.

### Install:
    `cd ~`\n
    `git clone https://github.com/cosmicc/spool-manager.git`\n
    `cd spool-manager`\n
    `./install.sh`\n

Python Requirements:
  Python 3.7+
  pandas (installed from install.sh)
  hx711 (installed from install.sh)
  
### Klipper Configuration:
  *Uses klippers save_variables config option.*

  **Add to klipper's printer.cfg:**
  
  `[save_variables]`
  `filename: ~/klipper_config/saved_vars.cfg`
  
  `[gcode_shell_command spool]
  command: ~/spool-manager/spool.py
  timeout: 10
  verbose: True

  [gcode_shell_command calibrate_weight]
  command: ~/spool-manager/calibrate.py
  timeout: 30
  verbose: True`

  **Add to klipper's printer.cfg (or wherever you put your klipper gcode macros)**
  
  ` 
  `

  **Other klipper gcode examples:**
    To come.

  Uses gcode_shell_command.py extras script.  This will need to be copied to klippers/klippy/extras directory

The calibrate option is used to calibrate the weight sensors with a known calibration weight specified in the saved_vars.cfgfile


### Todo & Potential Features:
  - [ ] Add a way to add new spools/edit spool data manually
  - [ ] Possibly move to mysql lite or postgresql database instead of saved csv data
  - [ ] Will have to create a csv export option if moved to real database backend
  - [ ] Add gcode execute before calibration to shut off any lights, fans, motors, heat
  - [ ] Add gcode option to modify calibration_weight option
  - [ ] Add gcode option to modify distance_to_extruder option
  - [ ] Add gcode option to modify extra_weight option
  

