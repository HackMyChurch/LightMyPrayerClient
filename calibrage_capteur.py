#!/usr/bin/env python
##################################################################
#               L I G H T   M Y   P R A Y E R 
#
#                      Calibrage du capteur
#
##################################################################
from raspiomix import Raspiomix
import RPi.GPIO as GPIO
import time
import ConfigParser

# Carte Raspiomix
r = Raspiomix()
GPIO.setmode(GPIO.BOARD)
# Capteur presence galet, capteur sur entree analogique 0
ir_sensor = 0
# 
cfg = ConfigParser.ConfigParser()

# Variables de seuil pour la detection 
seuil_detection_trappe = 0
seuil_detection_main   = 0
seuil_detection_galet  = 0
last_detection_value   = seuil_detection_trappe
detection_value = 0

def print_values():
	print ('Valeurs de calibration : ')
	print ('--------------------------------------------')
	print ("seuil_detection_trappe = " + str(seuil_detection_trappe))
	print ("seuil_detection_galet  = " + str(seuil_detection_galet))
	print ("seuil_detection_main   = " + str(seuil_detection_main))
	print ('--------------------------------------------')
	print ("Valeur lue = " +  str(detection_value))
	stone_detection()
	print ('--------------------------------------------')

def stone_detection():
	global detection_value, last_detection_value, seuil_detection_trappe, seuil_detection_main, seuil_detection_galet
	if detection_value > seuil_detection_trappe:
		if detection_value > seuil_detection_main:
			print(" --> Main ! (%f)" % detection_value)
			last_detection_value = detection_value
		else:
			if detection_value > seuil_detection_galet:
				print (" --> Galet (%f)" % detection_value)
				last_detection_value = seuil_detection_trappe
	else:
		print(" --> Trappe ! (%f)" % detection_value)

while True:
	try:
		detection_value = r.readAdc(ir_sensor)
		stone_detection()
		print_values()
		time.sleep(1)
		# relire le fichier de conf
		cfg.read('config/lmp.conf')
		seuil_detection_trappe = cfg.getfloat('sensor_calibration', 'seuil_detection_trappe')
		seuil_detection_main   = cfg.getfloat('sensor_calibration', 'seuil_detection_main')
		seuil_detection_galet  = cfg.getfloat('sensor_calibration', 'seuil_detection_galet')

	except KeyboardInterrupt:
		break

