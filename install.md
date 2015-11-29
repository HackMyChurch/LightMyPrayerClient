# Installation LightMyPrayer / Partie Raspberry

## System
- Installation Raspbian

## Package debian
	- Pi Cam
		`sudo apt-get update`
		`sudo apt-get install python-picamera`
		`sudo apt-get install daemon`
		`sudo apt-get install chkconfig`
	- http
		`sudo pip install requests`

## Starting fcserver at boot

To make the fcserver program start automatically when the system boots
- Copy bash script `scripts/fcserver` in `/etc/init.d` directory
- Register fcserver bash script with the command `sudo chkconfig --add fcserver`

## Starting python client at startup

- Edit `/etc/inittab` file and find the following line :
	`1:2345:respawn:/sbin/getty --noclear 38400 tty1 `
- comment it and replace by the following line :
	`1:2345:respawn:/bin/login -f pi tty1 </dev/tty1 >/dev/tty1 2>&1`

This forces the Raspberry Pi to autologin on `pi` user.

- Edit `/home/pi/.bashrc` and add the following line at the end of file
	`. /home/pi/lmp/scripts/run.sh`


More documentation at http://www.opentechguides.com/how-to/article/raspberry-pi/5/raspberry-pi-auto-start.html

## Setting Rasp1 in DHCP/DNS mode

- copy file `/home/pi/lmp/config/dnsmasq.conf` in `/etc/dnsmasq.conf`
- On Rasp1 , add service start at boot `sudo chkconfig --add dnsmasq`