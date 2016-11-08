###############################################################################
# Light My Prayer Automation
###############################################################################
#
# Starting up automatically LightMyPrayer Client if we are logged on TTY1
# Nothing is done if we are logged over ssh
#
#
###############################################################################
log="/tmp/lmpclient.log"
if [ "x$L1" = "xtty1" ]; then
	clear
	echo "   __ _       _     _                      ___                           "
	echo "  / /(_) __ _| |__ | |_    /\/\  _   _    / _ \_ __ __ _ _   _  ___ _ __ "
	echo " / / | |/ _\` | '_ \| __|  /    \| | | |  / /_)/ '__/ _\` | | | |/ _ \ '__|"
	echo "/ /__| | (_| | | | | |_  / /\/\ \ |_| | / ___/| | | (_| | |_| |  __/ |   "
	echo "\____/_|\__, |_| |_|\__| \/    \/\__, | \/    |_|  \__,_|\__, |\___|_|   "
	echo "        |___/                    |___/                   |___/           "
	cd /home/pi/lmp
	python LMPmonitor.py &
	# Echoing and Saving Both Stdout And Stderr
	# http://www.skorks.com/2009/09/using-bash-to-output-to-screen-and-file-at-the-same-time/
	# Option -u pour être en mode 'unbuffered' et envoyer tout de suite sur la sortie standard 
	sudo python client.py 1>>$log 2>>$log
else
  echo "LMP Client not launched : We're not on tty1. Are you in remote ssh ?"
fi



