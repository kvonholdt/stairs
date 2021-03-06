import csv
import logging
import socket
import sqlite3
import sys
import time
import thread
import requests
import json

from collections import namedtuple
from datetime import datetime
from gpiozero import MotionSensor
from neopixel import *

DEBUG = False
LIGHT = True
HOSTNAME = socket.gethostname()

# LED strip configuration:
LED_COUNT      = 30
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 5
LED_BRIGHTNESS = 120
LED_INVERT     = True
LED_CHANNEL    = 0
LED_STRIP      = ws.WS2812_STRIP

type = 'stairs'
url = 'http://srvgvm18.offis.uni-oldenburg.de:8443/entry'

class Database(object):
    '''
    Database class. Currently using sqlite3.
    '''
    def __init__(self):
        self.db = 'stairs.db'
        cnx = sqlite3.connect(self.db)
        cursor = cnx.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS entry (timestamp INTEGER NOT NULL, count INTEGER NOT NULL, type VARCHAR(250) NOT NULL, PRIMARY KEY (timestamp), UNIQUE(timestamp))''')
        cnx.commit()
        cnx.close()

    def save_entry(self, timestamp, count):
        '''
        Save the given timestamp into the database.
        '''
        cnx = sqlite3.connect(self.db)
        cursor = cnx.cursor()
        cursor.execute('INSERT OR IGNORE INTO entry VALUES (?, ?, ?)', [timestamp, count, type])
        cnx.commit()

		
def running_light(strip, color, width = 5, wait_ms = 200):
    '''
	Activates the running light on the LED strip
	'''
    print('running light')
    for i in range(1-width, strip.numPixels()):
        if i-1 >= 0:
            strip.setPixelColor(i-1, 0)	
        if i+width-1 < strip.numPixels():
            strip.setPixelColor(i+width-1, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
    strip.setPixelColor(strip.numPixels()-1, 0)
    strip.show()


def main():
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    strip.begin()
    logging.basicConfig(filename='stairs.log', level=logging.INFO, format='%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s')
    logging.info('start scanning')
    pir = MotionSensor(4)
    output = None
    if DEBUG:
        output = open(name='stairs.csv', mode='w', buffering=0)
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['timestamp'])
    else:
        db = Database()
    try:
        no_motion = True
        while True:
            pir.wait_for_motion()
            timestamp = int(datetime.now().strftime('%s')) * 1000
            payload = {'timestamp': timestamp, 'count': 1, 'type': type}
            r = requests.post(url, json=payload)
            pir.wait_for_no_motion()
            if DEBUG:
                writer.writerow([timestamp])
            else:
                db.save_entry(timestamp, 1)
                if LIGHT:
                    thread.start_new_thread( running_light, (strip, Color(255, 0, 0)))
    except KeyboardInterrupt:
        logging.info('closing scanner...')
        if output:
            output.close()


if __name__ == '__main__':
    main()
