###############################################################################
# Light My Prayer Automation
###############################################################################
#
# Starting up automatically LightMyPrayer Client if we are logged on TTY1
# Nothing is done if we are logged over ssh
#
#
###############################################################################
if [ "x$L1" = "xtty1" ]; then
	clear
	echo "   __ _       _     _                      ___                           "
	echo "  / /(_) __ _| |__ | |_    /\/\  _   _    / _ \_ __ __ _ _   _  ___ _ __ "
	echo " / / | |/ _\` | '_ \| __|  /    \| | | |  / /_)/ '__/ _\` | | | |/ _ \ '__|"
	echo "/ /__| | (_| | | | | |_  / /\/\ \ |_| | / ___/| | | (_| | |_| |  __/ |   "
	echo "\____/_|\__, |_| |_|\__| \/    \/\__, | \/    |_|  \__,_|\__, |\___|_|   "
	echo "        |___/                    |___/                   |___/           "
	cd /home/pi/lmp
	# Echoing and Saving Both Stdout And Stderr
	# http://www.skorks.com/2009/09/using-bash-to-output-to-screen-and-file-at-the-same-time/
	# sudo python client.py 2>&1 | tee /tmp/LMP_client.log
	sudo python client.py
else
  echo "LMP Client not launched : We're not on tty1. Are you in remote ssh ?"
fi



