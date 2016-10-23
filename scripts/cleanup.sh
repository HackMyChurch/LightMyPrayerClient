###############################################################################
# Light My Prayer Automation
###############################################################################
#
#	Cleanup Script
#
###############################################################################
echo "cleaning all pictures taken before"
rm -f /home/pi/lmp/img/rasp*.jpg
echo "cleaning lmp log"
rm -f /tmp/lmpclient.log
touch /tmp/lmpclient.log
echo "cleaning epiphany cahe"
rm -f home/pi/.cache/epiphany-browser/*
echo "cleaning trash"
rm -f /home/pi/.local/share/Trash/files/*
rm -f /home/pi/.local/share/Trash/info/*