# LightMyPrayerClient
Client Light My Prayer en Python pour Raspberry PI &amp; Raspiomix+

Including OPC feature to control LED via fadeCandy driver

## Leds control : FadeCandy, OPC
All code required to control LEDs are from this repo
https://github.com/scanlime/fadecandy

Controlling LEDS example
https://learn.adafruit.com/1500-neopixel-led-curtain-with-raspberry-pi-fadecandy/fadecandy-server-setup

### Introduction to opc via start instructions
First start the fcserver located in fcserver folder via command line : fcserver fcserv.json.

As mentionned in curtain example

To make the fcserver program start automatically when the system boots
```
sudo nano /etc/rc.local.
```
Just above the final “exit 0” line, copy and paste the following
```
/usr/local/bin/fcserver /usr/local/bin/fcserver.json >/var/log/fcserver.log 2>&1 &
```

Then use opc class described into <b>opc.py</b> in your code as into the <b>LEDLmp class</b>

Declare a client
```python
client = opc.Client('localhost:7890')
```
then put the number of pixels awaited by the fadecandy (512 pixels per fadecandy)
```python
pixels = [ (r,g,b) ] * self.numLEDs
self.client.put_pixels(pixels)
```
