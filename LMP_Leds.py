#!/usr/bin/env python

# Open Pixel Control client: All lights to solid white

import opc
import math, time, datetime
import pygame



#################################################################
# Global variables
#################################################################
black = [ (0,0,0) ]
white = [ (255,255,255) ]

#################################################################
# Class able to drive Leds
#################################################################
class LMPLed:

    numLEDs = 512
    client = opc.Client('localhost:7890')

    ledsColor = black
    brightness = 1.0

    startLedsTime = datetime.datetime.now()
    # Period for waiting mode
    waitingPeriod = 10.0
    # Time for fade
    fadeTime = datetime.datetime.now()
    fadePeriod = 5.0
    fadeDirection = 1.0
    
    isWaiting = True
    
    #constructor
    # set all leds to black
    def __init__(self):
        self.setColor(black)
        self.update()

    # set the new color of leds (depneding to brightness
    def setColor(self, color):
        self.ledsColor = color
        #print("color is : " + str(self.ledsColor))

    # set the global brightness
    def setBrightness(self, brightness):
        self.brightness = brightness

    # fade leds to full brightness
    def fadeIn(self):
        self.isWaiting = False
        self.fadeTime = datetime.datetime.now()
        self.fadeDirection = 1.0
        
    # fade leds to full brightness
    def fadeOut(self):
        self.isWaiting = False
        self.fadeTime = datetime.datetime.now()
        self.fadeDirection = -1.0
        
    ################################################################################
    # gives the ratio for waiting mode
    # calclucation base dof the difference betwenn satrt moment and current moment
    # with a little smooth effect based on sinus
    ################################################################################
    def waitingRatio(self):

        waitingRatio = 0.0
        
        # calculate the current time, and the fade ration depending on it
        currentTime = datetime.datetime.now()
        diffTime = currentTime - self.startLedsTime

        waitingRatio = (diffTime.total_seconds() % self.waitingPeriod) / self.waitingPeriod
        waitingRatio = math.fabs(math.sin(waitingRatio * 2*math.pi))

        return waitingRatio

    ################################################################################
    # gives the ratio for fade ratio
    # calculation based on the difference between start moment and current moment
    # with a little smooth effect based on sinus
    ################################################################################
    def fadeRatio(self):

        fadeRatio = 0.0
        
        # calculate the current time, and the fade ration depending on it
        currentTime = datetime.datetime.now()
        diffTime = currentTime - self.fadeTime

        fadeRatio = diffTime.total_seconds() / self.fadePeriod
        #fadeRatio = math.fabs(math.sin(fadeRatio * 2*math.pi))

        return fadeRatio
        
    def update(self):

        
        ratioTime=0.0

        if(self.isWaiting == True):
            print("leds waiting : " + str(datetime.datetime.now()))
            ratioTime = self.waitingRatio()
        else:
            print("leds fading : " + str(datetime.datetime.now()))
            ratioTime = self.fadeRatio()
            
        # Brightness is ratio ;)
        # print("Cureent Birghtness : " + str(ratioTime))
        self.setBrightness(ratioTime)

        # send the color to the strip
        r = self.ledsColor[0][0]* self.brightness
        g = self.ledsColor[0][1]* self.brightness
        b = self.ledsColor[0][2]* self.brightness

        pixels = [ (r,g,b) ] * self.numLEDs
        self.client.put_pixels(pixels)

           
#################################################################
#Main test loop
#################################################################
    
leds = LMPLed() # LEDS driver
leds.setColor(white)

pygame.init()
fen = pygame.display.set_mode((40,40))

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYUP:
            print("event : " + str(event.key))
            
            if event.key == pygame.K_UP:
                print("UP is : " + str(pygame.K_UP))
                leds.fadeIn()

            if event.key == pygame.K_DOWN:
                print("DOWN is : " + str(pygame.K_DOWN))
                leds.fadeOut()
            
    # Fade to white
    leds.update()

        
        
    
