###############################################################################
# Light My Prayer Automation
###############################################################################
#
# Stop LightMyPrayer Client
#
###############################################################################
ps aux | grep "sudo python client.py" | grep -v "grep" | while read user pid z
do
	echo "Stopping LMP Client (pid=$pid)"
	sudo kill -TERM $pid
done