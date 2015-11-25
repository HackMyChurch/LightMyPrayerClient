#!/usr/bin/env python
##################################################################
#               L I G H T   M Y   P R A Y E R 
#
# Gestion du Servo : http://razzpisampler.oreilly.com/ch05.html
#
# Il faut que la cam soit au moins a 25 cm du galet.
##################################################################
from raspiomix import Raspiomix
import RPi.GPIO as GPIO
import time
import picamera
import requests
import ConfigParser
import os
import LMPLed

CONFIG_FILE = "config/lmp.conf"
IMG_CONFIG_FILE = "config/img_index.conf"

# Lecture du fichier de configuration
cfg = ConfigParser.ConfigParser()
cfg.read(CONFIG_FILE)

# Lecture du dernier index des images
cfgimg = ConfigParser.ConfigParser()
cfgimg.read(IMG_CONFIG_FILE)

# Urls Serveur
url_upload = cfg.get('server', 'url_upload')

# Temps d'attente du scenario
wait_after_pic   = cfg.getfloat('client', 'wait_after_pic')
wait_after_open  = cfg.getfloat('client', 'wait_after_open')
wait_after_cycle = cfg.getfloat('client', 'wait_after_cycle')

# Temps d'animation de leds
fade_in_time  = cfg.getfloat('leds', 'fade_in_time')
fade_out_time = cfg.getfloat('leds', 'fade_out_time')
wait_time     = cfg.getfloat('leds', 'wait_time')

# Variables de seuil pour la detection
seuil_detection_trappe = cfg.getfloat('sensor_calibration', 'seuil_detection_trappe')
seuil_detection_main   = cfg.getfloat('sensor_calibration', 'seuil_detection_main')
seuil_detection_galet  = cfg.getfloat('sensor_calibration', 'seuil_detection_galet')

last_detection_value = seuil_detection_trappe

# Carte Raspiomix
r = Raspiomix()
GPIO.setmode(GPIO.BOARD)
# Pilotage servo
GPIO.setup(r.IO0, GPIO.OUT) # Mode board = 12, GPIO18
# Capteur presence galet, capteur sur entree analogique 0
ir_sensor = 0
# Pilotage Servo-moteur
pwm = GPIO.PWM(r.IO0, 100)
# Index des images
idx = cfgimg.getint('images', 'next_img_index')
# Repertoire des images
img_dir = cfg.get('client', 'img_dir')
# Etat du servo de la trappe
is_locked = True

# Pilotage des LEDS ###########################################################
leds = LMPLed.LMPLed() # LEDS driver
leds.setColor(leds.WHITE)
###############################################################################

# Hack pour recuperer l'ip du client.
def get_lan_last_ip_num():
	# Hackish function to get ip addr on linux...
    ip = os.popen("ifconfig eth0 | grep 'inet'").read().split(':')[1]
    ip = str(ip).split(' ')[0]
    last_ip_num = str(ip).split('.')[3]
    return last_ip_num

# Genere un numero de session pour avoir un nom d'image unique 
client_name = "raspberry-" + get_lan_last_ip_num()

def update(angle):
	# Valeurs calibrees de maniere empirique
  	duty = float(angle) / 8.8 + 2.5
	pwm.start(5)
	pwm.ChangeDutyCycle(duty)
	pwm.stop

def close_the_door():
	print "Lock lock lockin' the heaven door..."
	update(180)
	is_locked = True

def open_the_door():
	print "Stairway to heaven..."
	update(90)
	is_locked = False

def capture_image(i):
	# fixer la lumiere
	leds.fix()
	with picamera.PiCamera() as cam:
		print "Takin' a pic..."
		# Prendre la photo
		cam.start_preview()
		image_name = client_name + '_%03d.jpg' % i
		cam.capture(img_dir + '/' + image_name)
		cam.stop_preview()
		return image_name

def save_next_img_index():
	global idx
	idx += 1
	cfgimg.set('images', 'next_img_index', idx)
	write_config()

def stone_detection():
	global last_detection_value
	ok_for_taking_pic = False
	detection_value = r.readAdc(ir_sensor)
	print ("Value (%f)" % detection_value)
	if detection_value > seuil_detection_trappe:
		if detection_value > seuil_detection_main:
			print("Hand is here ! (%f)" % detection_value)
			last_detection_value = detection_value
			ok_for_taking_pic = False
		else:
			if last_detection_value > seuil_detection_galet:
				print ("Stone detected (%f)" % detection_value)
				# Allumer progressivement
				leds.fadeIn(fade_in_time)
				# ici on remet la valeur precedente a la valeur de la trappe
				# pour eviter de prendre en compte les oscillations
				last_detection_value = seuil_detection_trappe
				ok_for_taking_pic =  True
			
	return ok_for_taking_pic	

def post_picture(name):
	# Eteindre progressivement les LEDs
	leds.fadeOut(fade_out_time)
	try:
		if url_upload != "":
			data = { 'image':  open(img_dir + '/' + name) }
			r = requests.post(url_upload, files=data)
			print(r.json)
	except requests.exceptions.ConnectionError:
		print ("ERROR : Can't upload pic. Server is probably down !")

def write_config():
	cfgimg.write(open(IMG_CONFIG_FILE,'w'))

##################################################################
# Etat initial
close_the_door()
last_detection_value = seuil_detection_trappe

##################################################################
while True:
	try:
		# 1. Voir si l'on detecte une main qui pose le galet
		print "Waiting for some prayers..."
		if stone_detection():
			# 2. Prendre un photo du galet
			img = capture_image(idx)
			post_picture(img)
			# 3. Sauvegarder l'index de la prochaine image
			save_next_img_index()
			# 4. Petite tempo pour permettre le traitement de la capture
			time.sleep(wait_after_pic)
			# 5. Faire tomber le galet
			open_the_door()
			# 6. Temporiser juste assez pour avoir le rebond de la trappe
			time.sleep(wait_after_open)
			# 7. Refermer la trappe
			close_the_door()
		# Mode wait pour les leds
		leds.wait(2.0)
		# Tempo de fin de cycle.
		time.sleep(wait_after_cycle)
	# Quit on Ctrl+C
	except KeyboardInterrupt:
		close_the_door()
		write_config()
		GPIO.cleanup()
		break

