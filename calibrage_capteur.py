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
# seuil_detection_galet  = cfg.getfloat('sensor_calibration', 'seuil_detection_galet')

last_detection_value = seuil_detection_trappe

# Carte Raspiomix
r = Raspiomix()
GPIO.setmode(GPIO.BOARD)
# Pilotage servo
GPIO.setup(r.IO0, GPIO.OUT) # Mode board = 12, GPIO18
# Capteur presence galet, capteur sur entree analogique 0
ir_sensor = 0
# Pilotage Servo-moteur
motor = GPIO.PWM(r.IO0, 50)

#cfgimg.getint('images', 'next_img_index')

# Repertoire des images
img_dir = cfg.get('client', 'img_dir')
# Etape courante 
state = 'wait'
#
waiting_led_launched = False

# Pilotage des LEDS ###########################################################
leds = LMPLed.LMPLed() # LEDS driver
leds.setColor(leds.WHITE)
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
# Ouverture et fermeture de la porte par pilotage du servo-moteur en pwm
#
# def open_close():
# 	Frequency = 50             # Hz = 20ms de cycle
# 	Percent_Duty_Cycle_Mini = Frequency/10  #=5=1ms c'est un raccourci pour faire 1/50=20ms et prendre 5% (1ms)
# 	# on change le dutycycle a 1ms (1ms*1) pour aller a fond a gauche
# 	motor.start(Percent_Duty_Cycle_Mini*1) 
# 	time.sleep(1)
# 	# 1ms * 2 = 2 ms on demarre a fond a droite
# 	motor.ChangeDutyCycle(Percent_Duty_Cycle_Mini*2)
# 	time.sleep(1)
# 	# on change le dutycycle a 1ms (1ms*1) pour aller a fond a gauche
# 	motor.ChangeDutyCycle(Percent_Duty_Cycle_Mini*1) 
# 	time.sleep(wait_after_cycle)


#
# Predre la photo du galet en tenant compte des reglages fait en configuration
#
def capture_image():
	# fixer la lumiere
	leds.fix(1.0)
	image_name = client_name + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'
	print "Takin' a pic. File is " + image_name
	# with picamera.PiCamera() as cam:
	# 	cam.resolution = (cfg.getint('camera', 'resolution_h'), cfg.getint('camera', 'resolution_v'))
	# 	cam.sharpness = cfg.getint('camera', 'sharpness')
	# 	cam.contrast = cfg.getint('camera', 'contrast')
	# 	cam.brightness = cfg.getint('camera', 'brightness')
	# 	cam.saturation = cfg.getint('camera', 'saturation')
	# 	cam.ISO = cfg.getint('camera', 'ISO')
	# 	cam.video_stabilization = cfg.getboolean('camera', 'video_stabilization')
	# 	cam.exposure_compensation = cfg.getint('camera', 'exposure_compensation')
	# 	cam.exposure_mode = cfg.get('camera', 'exposure_mode')
	# 	cam.meter_mode = cfg.get('camera', 'meter_mode')
	# 	cam.awb_mode = cfg.get('camera', 'awb_mode')
	# 	cam.image_effect = cfg.get('camera', 'image_effect')
	# 	cam.color_effects = (cfg.getint('camera', 'color_effects_1'), cfg.getint('camera', 'color_effects_2'))
	# 	cam.rotation = cfg.getint('camera', 'rotation')
	# 	cam.hflip = cfg.getboolean('camera', 'hflip')
	# 	cam.vflip = cfg.getboolean('camera', 'vflip')
	# 	# Prendre la photo
	# 	cam.start_preview()
	# 	cam.capture(img_dir + '/' + image_name)
	# 	cam.stop_preview()
	return image_name

#
# Algo de detaction du galet
# Si la valeur du catpeur est superieur au seuil de detection de la trappe
# on regarder si l'on detecte une main ou un galet (differences de seuil)
# Il faut donc aussi comparer la valeur lue avec la precedente, 
# ce qui permet de detecter la main, et de ne prendre la photo que par la suite
#
#                 main
#               /-------------\    galet
#  trappe      /               \____________ 
#  ___________/
#
# def stone_detection():
# 	global detection_value, last_detection_value, seuil_detection_trappe, seuil_detection_main, seuil_detection_galet, state, waiting_led_launched
# 	ok_for_taking_pic = False
# 	state = 'wait'
# 	if detection_value > seuil_detection_trappe:
# 		if detection_value > seuil_detection_main:
# 			print("Hand is here ! (%f)" % detection_value)
# 			state = 'hand'
# 			last_detection_value = detection_value
# 			ok_for_taking_pic = False
# 		else:
# 			if last_detection_value > seuil_detection_galet:
# 				print ("Stone detected (%f)" % detection_value)
# 				state = 'stone'
# 				# Allumer progressivement
# 				leds.fadeIn(fade_in_time)
# 				while not leds.fadeIsDone:
# 					leds.update()

# 				# On change d'etat de leds alors waiting_led_launched doit changer
# 				waiting_led_launched = False
# 				# ici on remet la valeur precedente a la valeur de la trappe
# 				# pour eviter de prendre en compte les oscillations
# 				last_detection_value = seuil_detection_trappe
# 				ok_for_taking_pic =  True
			
# 	return ok_for_taking_pic
	
def stone_detection():
	global last_detection_value, state, waiting_led_launched
	ok_for_taking_pic = False
	detection_value = r.readAdc(ir_sensor)
	state = 'wait'
	# Si on detecte un front montant
	if detection_value > seuil_detection_main:
		print("Hand is here ! (%f)" % detection_value)
		state = 'hand'
		last_detection_value = detection_value
		ok_for_taking_pic = False
	else:
		# ici plus ou pas de main : on regarde si la valeur precedente etait une main
		if last_detection_value < seuil_detection_main:
			print ("Stone detected (%f)" % detection_value)
			state = 'stone'
			# Allumer progressivement
			leds.fadeIn(fade_in_time)
			while not leds.fadeIsDone:
				leds.update()

			# On change d'etat de leds alors waiting_led_launched doit changer
			waiting_led_launched = False
			last_detection_value = seuil_detection_trappe
			ok_for_taking_pic =  True
			
	return ok_for_taking_pic	
#
# Poster l'image au serveur de diffusion
#
def post_picture(name):
	# Eteindre progressivement les LEDs
	leds.fadeOut(fade_out_time)
	while not leds.fadeIsDone:
		leds.update()

	try:
		# if url_upload != "":
		# 	data = { 'image':  open(img_dir + '/' + name) }
		# 	r = requests.post(url_upload, files=data)
		# 	print(r.json)
		print "Posting photo..."
	except requests.exceptions.ConnectionError:
		print ("ERROR : Can't upload pic. Server is probably down !")

def print_values():
	print ('Valeurs de calibration : ')
	print ('--------------------------------------------')
	print ("seuil_detection_trappe = " + str(seuil_detection_trappe))
	# print ("seuil_detection_galet  = " + str(seuil_detection_galet))
	print ("seuil_detection_main   = " + str(seuil_detection_main))
	print ('--------------------------------------------')
	print ("Valeur lue = " +  str(detection_value))
	stone_detection()
	print ('--------------------------------------------')

##################################################################
# Etat initial
# open_close()
last_detection_value = seuil_detection_trappe
state = 'wait'

########################## M A I N ###############################
while True:
	try:
		detection_value = r.readAdc(ir_sensor)

		# 1. Voir si l'on detecte une main qui pose le galet
		# Mode wait pour les leds
		if state == 'wait':
			if not waiting_led_launched:
				print "Waiting for some prayers..."
				leds.wait(wait_time)
				waiting_led_launched = True

		if stone_detection():
			# 2. Prendre un photo du galet
			img = capture_image()
			post_picture(img)
			# 3. Petite tempo pour permettre le traitement de la capture
			time.sleep(wait_after_pic)
			# 4. Faire tomber le galet
			# open_close()
		# 5. Tempo de fin de cycle.
		time.sleep(wait_after_cycle)
		leds.update()

		cfg.read('config/lmp.conf')
		seuil_detection_trappe = cfg.getfloat('sensor_calibration', 'seuil_detection_trappe')
		seuil_detection_main   = cfg.getfloat('sensor_calibration', 'seuil_detection_main')
		# seuil_detection_galet  = cfg.getfloat('sensor_calibration', 'seuil_detection_galet')
		wait_time = cfg.getfloat('leds', 'wait_time')
		print_values()
		time.sleep(0.5)
	# Quit on Ctrl+C
	except KeyboardInterrupt:
		leds.setColor(leds.BLACK)
		leds.update()
		# open_close()
		# time.sleep(2)
		# GPIO.cleanup()
		break

