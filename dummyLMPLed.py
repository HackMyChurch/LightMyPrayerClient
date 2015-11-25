#!/usr/bin/env python

import pygame
import LMPLed
           
#################################################################
#Main test loop
#################################################################
    
leds = LMPLed.LMPLed() # LEDS driver
leds.setColor(leds.WHITE)

pygame.init()
fen = pygame.display.set_mode((200,200))

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYUP:
            print("eventKey : " + str(event.key))
            
            if event.key == pygame.K_UP:
                leds.fadeIn(10.0)

            if event.key == pygame.K_DOWN:
                leds.fadeOut(5.0)
                
            if event.key == pygame.K_LEFT:
                leds.fix()
                
            if event.key == pygame.K_RIGHT:
                leds.wait(2.0)
            
    # Fade to white
    leds.update()

    if(leds.fadeIsDone==True):
        leds.wait(10.0)
        leds.fadeIsDone = False

        
        
    
