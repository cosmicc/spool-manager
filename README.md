# spool-manager
Ultimate Weighted Spool Manager for Klipper

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
