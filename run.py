import blescan
import csv
import logging
import socket
import sqlite3
import sys
import time

from collections import namedtuple
from datetime import datetime
from gpiozero import MotionSensor
from neopixel import *

DEBUG = True 
HOSTNAME = socket.gethostname()

# LED strip configuration:
LED_COUNT      = 150               # Number of LED pixels.
LED_PIN        = 18                # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000            # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5                 # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 0                 # Set to 0 for darkest and 255 for brightest
LED_INVERT     = True              # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0                 # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2812_STRIP   # Strip type and colour ordering

class Database(object):
    '''
    Database class. Currently using sqlite3.
    '''
    def __init__(self):
        self.db = 'stairs.db'
        cnx = sqlite3.connect(self.db)
        cursor = cnx.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS entry (timestamp INTEGER, UNIQUE(timestamp))''')
        cnx.commit()
        cnx.close()

    def save_entry(self, timestamp):
        '''
        Save the given timestamp into the database.
        '''
        cnx = sqlite3.connect(self.db)
        cursor = cnx.cursor()
        cursor.execute('INSERT OR IGNORE INTO entry VALUES (?)',
            timestamp)
        cnx.commit()

		
def running_light(strip, color, wait_ms = 200):
    '''
	Activates the running light on the LED strip
	'''
	for i in range(1, strip.numPixels()-1):
		strip.setPixelColor(i-1, color)
		strip.setPixelColor(i, color)		
		strip.setPixelColor(i+1, color)
		strip.show()
		time.sleep(wait_ms/1000.0)

def main():
	# Create NeoPixel object with appropriate configuration.
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
	# Intialize the library (must be called once before other functions).
	strip.begin()
    logging.basicConfig(filename='stairs.log', level=logging.INFO,
                        format='%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s')
    logging.info('start scanning')
    pir = MotionSensor(4)
    output = None
    if DEBUG:
        output = open(file='stairs.csv', mode='w', buffering=0)
        writer = csv.writer(output, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['timestamp'])
    else:
        db = Database()
    try:
        while True:
            if pir.motion_detected:
			    timestamp = int(datetime.now().strftime('%s')) * 1000
			    print(time.time())
				print(timestamp)
                if DEBUG:
                    writer.writerow(timestamp)
                else:
                    db.save_entry(timestamp)
				running_light(strip, Color(255, 0, 0))
            time.sleep(.2)
    except KeyboardInterrupt:
        logging.info('closing scanner...')
        if output:
            output.close()


if __name__ == '__main__':
    main()
