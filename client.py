##################################################################
#               L I G H T   M Y   P R A Y E R 
#
# Gestion du Servo : http://razzpisampler.oreilly.com/ch05.html
#
# Il faut que la cam soit au moins a 25 cm du galet.
##################################################################
from Tkinter import *
from raspiomix import Raspiomix
import RPi.GPIO as GPIO
import time
import picamera
import requests
import ConfigParser

# Lecture du fichier de configuration
cfg = ConfigParser.ConfigParser()
cfg.read('config/lmp.conf')

# Constantes
lmp_server = cfg.get('server', 'url')

wait_after_pic   = cfg.getfloat('client', 'wait_after_pic')
wait_after_open  = cfg.getfloat('client', 'wait_after_open')
wait_after_cycle = cfg.getfloat('client', 'wait_after_cycle')

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
idx = 0
# Etat du servo de la trappe
is_locked = True
# Repertoire des images
img_dir = cfg.get('client', 'img_dir')


# class App:

#    def __init__(self, master):
#        frame = Frame(master)
#        frame.pack()
#        scale = Scale(seuil_detection_trappe, from_=0, to=5,
#              orient=HORIZONTAL, command=self.update)
#        scale.grid(row=0)


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
    with picamera.PiCamera() as cam:
        print "Takin' a pic..."
        cam.start_preview()
        image_name = 'image_%03d.jpg' % i
        cam.capture(img_dir + '/' + image_name)
        cam.stop_preview()
        return image_name

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
				# ici on remet la valeur precedente a la valeur de la trappe
				# pour eviter de prendre en compte les oscillations
				last_detection_value = seuil_detection_trappe
				ok_for_taking_pic =  True
			
	return ok_for_taking_pic

def post_picture(name):
	try:
		if lmp_server != "":
			data = { 'image':  open(img_dir + '/' + name) }
			r = requests.post(lmp_server, files=data)
			print(r.json)
			print(r.text)
	except requests.exceptions.ConnectionError:
		print ("ERROR : Can't upload pic. Server is probably down !")

# root = Tk()
# root.wm_title('Controle des seuils de detection')
# app = App(root)
# root.geometry("200x50+0+0")
# root.mainloop()

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
			idx += 1
			time.sleep(wait_after_pic)
			# 3. Faire tomber le galet
			open_the_door()
			# 4. Refermer la trappe
			time.sleep(wait_after_open)
			close_the_door()
			
		time.sleep(wait_after_cycle)
	# Quit on Ctrl+C
	except KeyboardInterrupt:
		close_the_door()
		GPIO.cleanup()
		break
