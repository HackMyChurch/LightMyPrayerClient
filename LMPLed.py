#!/usr/bin/env python

# Open Pixel Control client: All lights to solid white

import opc
import math, time, datetime

debug_mode = False

#################################################################
# Class able to drive Leds
#################################################################
class LMPLed:
    BLACK = [ (0,0,0) ]
    WHITE = [ (255,255,255) ]
    MAGIC_PIXEL = 0 # Pixel fixe pour les besoin du scenario
    MAX_BRIGHTNESS_FOR_MP = 100.0 # Brillance max du magic pixel

    modeFix = "fix"
    modeWait = "wait"
    modeFadeIn = "fadeIn"
    modeFadeOut = "fadeOut"
    mode = modeFix

    numLEDs = 512
    client = opc.Client('localhost:7890')

    ledsColor = BLACK
    brightness = 1.0
    minBright = 0.1
    maxBright = 1.0

    startLedsTime = datetime.datetime.now()
    # Period for waiting mode
    waitPeriod = 10.0
    # Time for fade
    fadeTime = datetime.datetime.now()
    fadePeriod = 10.0
    fadeIsDone = False
    # fix the light
    fixBrightness = 0.0
    
    #constructor
    # set all leds to black
    def __init__(self):
        self.setColor(self.BLACK)
        self.update()

    # Logging de debug
    def debug_log(self, s):
        if debug_mode:
            print s

    # set the new color of leds (depneding to brightness
    def setColor(self, color):
        self.ledsColor = color
        #self.debug_log("color is : " + str(self.ledsColor))

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
        self.debug_log("WAITING Launched---------------")
        
    # fade leds to full brightness
    def fadeIn(self, period):
        self.fadePeriod = period
        self.mode = self.modeFadeIn
        self.fadeTime = datetime.datetime.now()
        self.debug_log("FADE IN Launched---------------")
        
    # fade leds to full brightness
    def fadeOut(self, period):
        self.fadePeriod = period
        self.mode = self.modeFadeOut
        self.fadeTime = datetime.datetime.now()
        self.debug_log("FADE OUT Launched---------------")
        
    # fade leds to full brightness
    def fix(self, bright):
        self.mode = self.modeFix
        self.fixBrightness = bright
        self.debug_log("FIX LIGHT Launched---------------")
        
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

        #self.debug_log("Waiting to the ratio " + str(waitingRatio))
        
        # return waitingRatio
        return self.mapValues(waitingRatio, 0.0, 1.0, 0.0, 0.25)

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

        #self.debug_log("Fading to the ratio " + str(fadeRatio) + ", isDone?" + str(self.fadeIsDone))
        
        return fadeRatio
    
    ################################################################################
    # gives the ratio for fade ratio
    # calculation based on the difference between start moment and current moment
    # with a little smooth effect based on sinus
    ################################################################################
    def fixRatio(self):

        return self.fixBrightness

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
            ratioTime = self.fixRatio()
            
        else:
            ratioTime = 0.0

        #ratioTime = self.brightness + ratioTime

        # self.debug_log("Ratio = " + str(ratioTime) + " : " + "brightness = " + str(self.brightness))
        
        # Brightness is ratio ;)
        # self.debug_log("Cureent Birghtness : " + str(ratioTime))
        self.setBrightness(ratioTime)

        # send the color to the strip
        r = self.ledsColor[0][0]* self.brightness
        g = self.ledsColor[0][1]* self.brightness
        b = self.ledsColor[0][2]* self.brightness

        pixels = [ (r,g,b) ] * self.numLEDs
        if(self.mode == self.modeWait):
            pixels[self.MAGIC_PIXEL] = (255, 255, 255)
        else:
            pixels[self.MAGIC_PIXEL] = (0, 0, 0)
        # pixels[self.MAGIC_PIXEL] = (int(self.MAX_BRIGHTNESS_FOR_MP - r), int(self.MAX_BRIGHTNESS_FOR_MP - g), int(self.MAX_BRIGHTNESS_FOR_MP - b)) 
        self.client.put_pixels(pixels)

