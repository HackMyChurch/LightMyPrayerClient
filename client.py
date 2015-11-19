##################################################################
#               L I G H T   M Y   P R A Y E R 
#
# Gestion du Servo : http://razzpisampler.oreilly.com/ch05.html
#
##################################################################
from Tkinter import *
from raspiomix import Raspiomix
import RPi.GPIO as GPIO
import time
import picamera

# Constantes
IMG_DIR = "/home/pi/lmp/img"

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
#
#    def __init__(self, master):
#        frame = Frame(master)
#        frame.pack()
#        scale = Scale(frame, from_=0, to=180,
#              orient=HORIZONTAL, command=self.update)
#        scale.grid(row=0)
#
def update(angle):
	# Valeurs calibrees de maniere empirique
  	duty = float(angle) / 8.8 + 2.5
	pwm.start(5)
	pwm.ChangeDutyCycle(duty)
	pwm.stop

def close():
	print "Lock lock lockin' the heaven door..."
	update(180)
	is_locked = True

def open():
	print "Stairway to heaven..."
	update(90)
	is_locked = False

def capture_image(i):
    with picamera.PiCamera() as cam:
        print "Takin' a pic..."
        cam.start_preview()
        cam.capture(IMG_DIR + '/image_%03d.jpg' % i)
        cam.stop_preview()

def stone_detection():
	val = r.readAdc(ir_sensor)
	if val > 0.03378:
		print ("Stone detected (%f)" % val)
		return True	

	return False

# root = Tk()
# root.wm_title('Servo Control')
# app = App(root)
# root.geometry("200x50+0+0")
# root.mainloop()

##################################################################
# Etat initial
close()

##################################################################
while True:
	try:
		# 1. Voir si l'on detecte une main qui pose le galet
		print "Waiting for some prayers..."
		if stone_detection():
			# 2. Prendre un photo du galet
			capture_image(idx)
			idx += 1
			time.sleep(2)
			# 3. Faire tomber le galet
			open()
			# 4. Refermer la trappe
			time.sleep(1)
			close()
			
		time.sleep(1)
	# Quit on Ctrl+C
	except KeyboardInterrupt:
		close()
		GPIO.cleanup()
		break
