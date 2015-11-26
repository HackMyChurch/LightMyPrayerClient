# Installation LightMyPrayer / Partie Raspberry

## Système
- Installation Raspbian

## Package debian
	- Gestion de la caméra
		`sudo apt-get update`
		`sudo apt-get install python-picamera`
		`sudo apt-get install daemon`
		`sudo apt-get install chkconfig`
	- Gestion de http
		`sudo pip install requests`

## Starting fcserver at boot

To make the fcserver program start automatically when the system boots
- Copy bash script `scripts/fcserver` in `/etc/init.d` directory
- Register fcserver bash script with the command `sudo chkconfig --add fcserver`
