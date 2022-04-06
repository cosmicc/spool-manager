# spool-manager
Weighted Spool Manager for Klipper
Utilizes the HX711 Load sensor to calculate and save filament data

Python Requirements:
  Pandas
  
Klipper Configuration:
  Add to klipper's printer.cfg:
  
  [save_variables]
  filename: ~/klipper_config/saved_vars.cfg
  
  [gcode_shell_command spool_change]
  command: ~/spool-manager/loadspool.py
  timeout: 5
  verbose: False
