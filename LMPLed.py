#!/usr/bin/env python

# Open Pixel Control client: All lights to solid white

import opc
import math, time, datetime

#################################################################
# Class able to drive Leds
#################################################################
class LMPLed:
    debug_mode = False
    BLACK = [ (0,0,0) ]
    WHITE = [ (255,255,255) ]
    RED = (255,0,0)
    GREEN = (0,255,0)
    MAGIC_PIXEL = 0 # Pixel fixe pour les besoins du scenario
    MAX_BRIGHTNESS_FOR_MP = 100.0 # Brillance max du magic pixel

    modeFix = "fix"
    modeWait = "wait"
    modeFadeIn = "fadeIn"
    modeFadeOut = "fadeOut"
    modeCommand = "Command"
    modeReboot = "Rebbot"
    modeShutdown = "Shutdown"
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
        if self.debug_mode:
            print s

    # set the new color of leds (depneding to brightness
    def setColor(self, color):
        self.ledsColor = color

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
        
    # Wait mode
    def wait(self, period):
        self.waitPeriod = period
        self.mode = self.modeWait
        self.debug_log("WAITING Launched---------------")
        
    # Fade In mode
    def fadeIn(self, period):
        self.fadePeriod = period
        self.mode = self.modeFadeIn
        self.fadeTime = datetime.datetime.now()
        self.debug_log("FADE IN Launched---------------")
        
    # Fade out mode
    def fadeOut(self, period):
        self.fadePeriod = period
        self.mode = self.modeFadeOut
        self.fadeTime = datetime.datetime.now()
        self.debug_log("FADE OUT Launched---------------")
        
    # Fix mode : no fade
    def fix(self, bright):
        self.mode = self.modeFix
        self.fixBrightness = bright
        self.debug_log("FIX LIGHT Launched---------------")
        
    # Command Mode
    def command(self, period):
        self.fadePeriod = period
        self.mode = self.modeCommand
        self.fadeTime = datetime.datetime.now()
        self.debug_log("COMMAND Launched---------------")
        
    # Shutdown Command mode
    def shutdown(self):
        self.mode = self.modeShutdown
        self.debug_log("COMMAND SHUTDOWN Launched---------------")
        
    # Reboot Command mode
    def reboot(self):
        self.mode = self.modeReboot
        self.debug_log("COMMAND REBOOT Launched---------------")
        
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
            ratioTime = self.waitingRatio()
            
        elif(self.mode == self.modeFadeIn):
            ratioTime = self.fadeRatio()
            
        elif(self.mode == self.modeFadeOut):
            ratioTime = 1 - self.fadeRatio()
            
        elif(self.mode == self.modeFix):
            ratioTime = self.fixRatio()

        elif(self.mode == self.modeCommand):
            ratioTime = self.waitingRatio()

        else:
            ratioTime = 0.0

        # Brightness is ratio ;)
        self.setBrightness(ratioTime)

        # send the color to the strip
        r = self.ledsColor[0][0]* self.brightness
        g = self.ledsColor[0][1]* self.brightness
        b = self.ledsColor[0][2]* self.brightness

        pixels = [ (r,g,b) ] * self.numLEDs

        # Gestion de la led MAGIC_PIXEL
        if(self.mode == self.modeWait):
            pixels[self.MAGIC_PIXEL] = (255, 255, 255)

        elif(self.mode == self.modeCommand or self.mode == self.modeShutdown):   
            pixels[self.MAGIC_PIXEL] = self.RED

        elif(self.mode == self.modeReboot):   
            pixels[self.MAGIC_PIXEL] = self.GREEN

        else:
            pixels[self.MAGIC_PIXEL] = (0, 0, 0)

        self.client.put_pixels(pixels)
