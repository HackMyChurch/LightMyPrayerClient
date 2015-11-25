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

# Constantes
IMG_DIR = "/home/pi/lmp/img"
# LMP_SERVER = "http://192.168.0.25:9292/lmp/image/upload"
LMP_SERVER = "http://192.168.1.59:9292/lmp/image/upload"
# LMP_SERVER = ""
WAIT_AFTER_PIC = 1
WAIT_AFTER_OPEN = 0.6
WAIT_AFTER_CYCLE = 1

# Variables de seuil pour la detection
seuil_detection_trappe = 1.550
seuil_detection_galet = 1.825
seuil_detection_main =  2.595

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
        cam.capture(IMG_DIR + '/' + image_name)
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
		if LMP_SERVER != "":
			data = { 'image':  open(IMG_DIR + '/' + name) }
			r = requests.post(LMP_SERVER, files=data)
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
			time.sleep(WAIT_AFTER_PIC)
			# 3. Faire tomber le galet
			open_the_door()
			# 4. Refermer la trappe
			time.sleep(WAIT_AFTER_OPEN)
			close_the_door()
			
		time.sleep(WAIT_AFTER_CYCLE)
	# Quit on Ctrl+C
	except KeyboardInterrupt:
		close_the_door()
		GPIO.cleanup()
		break
