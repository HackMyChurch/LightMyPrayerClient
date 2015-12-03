#!/usr/bin/env python
##################################################################
#               L I G H T   M Y   P R A Y E R 
# Calibration de la picam
#
##################################################################
import time
import datetime
import picamera
import requests
import ConfigParser
import os
import LMPLed

CONFIG_FILE = "config/lmp.conf"

# Lecture du fichier de configuration
cfg = ConfigParser.ConfigParser()
cfg.read(CONFIG_FILE)

# Urls Serveur
url_upload = cfg.get('server', 'url_upload')

# Repertoire des images
img_dir = cfg.get('client', 'img_dir')


# Pilotage des LEDS ###########################################################
leds = LMPLed.LMPLed() # LEDS driver
###############################################################################

#
# Hack pour recuperer l'ip du client.
#
def get_host_name():
	return os.popen('hostname').read().rstrip('\n\r ')

#
# Genere un numero de client pour avoir un nom d'image unique 
#
client_name = get_host_name()
print "Client name is '" + client_name + "'"


#
# Predre la photo du galet en tenant compte des reglages fait en configuration
#
def capture_image():
	# fixer la lumiere
	leds.fix()
	image_name = client_name + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'
	print "Takin' a pic. File is " + image_name
	with picamera.PiCamera() as cam:
		cam.resolution = (cfg.getint('camera', 'resolution_h'), cfg.getint('camera', 'resolution_v'))
		cam.sharpness = cfg.getint('camera', 'sharpness')
		cam.contrast = cfg.getint('camera', 'contrast')
		cam.brightness = cfg.getint('camera', 'brightness')
		cam.saturation = cfg.getint('camera', 'saturation')
		cam.ISO = cfg.getint('camera', 'ISO')
		cam.video_stabilization = cfg.getboolean('camera', 'video_stabilization')
		cam.exposure_compensation = cfg.getint('camera', 'exposure_compensation')
		cam.exposure_mode = cfg.get('camera', 'exposure_mode')
		cam.meter_mode = cfg.get('camera', 'meter_mode')
		cam.awb_mode = cfg.get('camera', 'awb_mode')
		cam.image_effect = cfg.get('camera', 'image_effect')
		cam.color_effects = (cfg.getint('camera', 'color_effects_1'), cfg.getint('camera', 'color_effects_2'))
		cam.rotation = cfg.getint('camera', 'rotation')
		cam.hflip = cfg.getboolean('camera', 'hflip')
		cam.vflip = cfg.getboolean('camera', 'vflip')
		# Prendre la photo
		cam.start_preview()
		cam.capture(img_dir + '/' + image_name)
		cam.stop_preview()
	return image_name

#
# Poster l'image au serveur de diffusion
#
def post_picture(name):
	# Eteindre progressivement les LEDs
	try:
		if url_upload != "":
			data = { 'image':  open(img_dir + '/' + name) }
			r = requests.post(url_upload, files=data)
			print(r.json)
	except requests.exceptions.ConnectionError:
		print ("ERROR : Can't upload pic. Server is probably down !")


leds.setColor(leds.WHITE)
leds.update()
########################## M A I N ###############################
while True:
	try:
		cfg.read('config/lmp.conf')

		inpout = ""
		inpout = raw_input("Take a pic ?")
		if inpout != "":
			leds.fadeIn(1)
			while not leds.fadeIsDone:
				leds.update()

			img = capture_image()
			post_picture(img)

	except KeyboardInterrupt:
		leds.setColor(leds.BLACK)
		leds.update()
		break

