#!/usr/bin/env python

import LMPLed
           
#################################################################
# Main test loop
#################################################################
    
leds = LMPLed.LMPLed() # LEDS driver
leds.fadeOut(2.0)
leds.setColor(leds.BLACK)