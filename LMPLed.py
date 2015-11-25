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

    modeFix = "fix"
    modeWait = "wait"
    modeFadeIn = "fadeIn"
    modeFadeOut = "fadeOut"
    mode = modeFix

    numLEDs = 512
    client = opc.Client('localhost:7890')

    ledsColor = black
    brightness = 1.0
    minBright = 0.2
    maxBright = 1.0

    startLedsTime = datetime.datetime.now()
    # Period for waiting mode
    waitPeriod = 10.0
    # Time for fade
    fadeTime = datetime.datetime.now()
    fadePeriod = 10.0
    fadeIsDone = False
    
    #constructor
    # set all leds to black
    def __init__(self):
        self.setColor(black)
        self.update()

    # set the new color of leds (depneding to brightness
    def setColor(self, color):
        self.ledsColor = color
        #print("color is : " + str(self.ledsColor))

    def mapValues(self, value, inputMin, inputMax, outputMin, outputMax):
        outVal = ((value - inputMin) / (inputMax - inputMin) * (outputMax - outputMin) + outputMin)
	
        if( outVal > outputMax ):
            outVal = outputMax;
        elif( outVal < outputMin ):
            outVal = outputMin

	return outVal
    
    # set the global brightness
    def setBrightness(self, brightness):
        self.brightness = self.mapValues(brightness, 0.0, 1.0, self.minBright, self.maxBright)
        #self.brightness = brightness
        
    # fade leds to full brightness
    def wait(self, period):
        self.waitPeriod = period
        self.mode = self.modeWait
        print("WAITING Launched---------------")
        
    # fade leds to full brightness
    def fadeIn(self, period):
        self.fadePeriod = period
        self.mode = self.modeFadeIn
        self.fadeTime = datetime.datetime.now()
        print("FADE IN Launched---------------")
        
    # fade leds to full brightness
    def fadeOut(self, period):
        self.fadePeriod = period
        self.mode = self.modeFadeOut
        self.fadeTime = datetime.datetime.now()
        print("FADE OUT Launched---------------")
        
    # fade leds to full brightness
    def fix(self):
        self.mode = self.modeFix
        print("FIX LIGHT Launched---------------")
        
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

        waitingRatio = (diffTime.total_seconds() % self.waitPeriod) / self.waitPeriod
        waitingRatio = math.fabs(math.sin(waitingRatio * 2*math.pi))

        #print("Waiting to the ratio " + str(waitingRatio))
        
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
        if(fadeRatio >= 1.0):
            self.fadeIsDone = True
        else:
            self.fadeIsDone = False

        #print("Fading to the ratio " + str(fadeRatio) + ", isDone?" + str(self.fadeIsDone))
        
        return fadeRatio

    ##########################################################################
    # calculates constantly the brightness and sets the leds
    # has to be constantly called in mainLoop to manage leds
    ##########################################################################
    def update(self):

        ratioTime = 0.0

        if(self.mode == self.modeWait):
            # Waing : chasing up and down
            ratioTime = self.waitingRatio()
            
        elif(self.mode == self.modeFadeIn):
            # Waiting : Fading up and stop
            ratioTime = self.fadeRatio()
            
        elif(self.mode == self.modeFadeOut):
            # Waiting : Fading up and stop
            ratioTime = 1 - self.fadeRatio()
            
        elif(self.mode == self.modeFix):
            # fix light
            ratioTime = 1.0
            
        else:
            ratioTime = 0.0

        #ratioTime = self.brightness + ratioTime

        # print("Ratio = " + str(ratioTime) + " : " + "brightness = " + str(self.brightness))
        
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
    
# leds = LMPLed() # LEDS driver
# leds.setColor(white)

# pygame.init()
# fen = pygame.display.set_mode((200,200))

# while True:
#     for event in pygame.event.get():
#         if event.type == pygame.KEYUP:
#             print("eventKey : " + str(event.key))
            
#             if event.key == pygame.K_UP:
#                 leds.fadeIn(10.0)

#             if event.key == pygame.K_DOWN:
#                 leds.fadeOut(5.0)
                
#             if event.key == pygame.K_LEFT:
#                 leds.fix()
                
#             if event.key == pygame.K_RIGHT:
#                 leds.wait(2.0)
            
#     # Fade to white
#     leds.update()

#     if(leds.fadeIsDone==True):
#         leds.wait(10.0)
#         leds.fadeIsDone = False

        
        
    
