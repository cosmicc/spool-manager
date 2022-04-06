echo -e "Spool-Manager for Klipper Installer script\n"
echo -n "Installing gcode shell command script to Klipper extras..."
cp gcode_shell_command.py ~/klipper/klippy/extras
echo " Complete"
echo -n "Installing Python requirements..."
pip3 -q install -r requirements.txt
echo " Complete"
