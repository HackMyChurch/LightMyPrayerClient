###############################################################################
# Light My Prayer Automation
###############################################################################
#
# Stop LightMyPrayer Client
#
###############################################################################
ps aux | grep "sudo python -u client.py" | grep -v "grep" | while read user pid z
do
	echo "Stopping LMP Client (pid=$pid)"
	sudo kill -TERM $pid
	cd /home/pi/lmp
	sudo python -u leds-stop.py
done