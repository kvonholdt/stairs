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
HOST = '169.254.214.44'
PORT = 2003
light = 0

# LED strip configuration:
LED_COUNT      = 150
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 5
LED_BRIGHTNESS = 255
LED_INVERT     = True
LED_CHANNEL    = 0
LED_STRIP      = ws.WS2812_STRIP

type = 'stairs'
url = 'http://srvgvm18.offis.uni-oldenburg.de:8443/entry'

print'start stairs programm'

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

def slow_light(strip, color, width = 10, wait_ms = 600):
    while True:
        if light == 0:
            for i in range(0,width):
                if light == 0:
                    if strip.numPixels()%width == i:
                        strip.setPixelColor(strip.numPixels()-1, 0)
                    for j in range(i, strip.numPixels(), width):
                        strip.setPixelColor(j, color)
                        strip.setPixelColor(j-1, 0)
                    strip.show()
                    time.sleep(wait_ms/1000.0)
        else:
            time.sleep(2)


		
def running_light(strip, color, width = 7, wait_ms = 100):
    '''
    Activates the running light on the LED strip
    '''
    print('running light')
    global light
    light = light +1
    for i in range(0, strip.numPixels()-1):
        strip.setPixelColor(i,0)
    strip.show()
    for i in range(1-width, strip.numPixels()+8):
        if i-1 >= 0 and i-1 < strip.numPixels():
            strip.setPixelColor(i-1, Color(126,0,0))
        if i-2 >= 0 and i-2 < strip.numPixels():
            strip.setPixelColor(i-2, Color(64,0,0))
        if i-3 >= 0 and i-3 < strip.numPixels():
            strip.setPixelColor(i-3, Color(32,0,0))
        if i-4 >= 0 and i-4 < strip.numPixels():
            strip.setPixelColor(i-4,Color(16,0,0))
        if i-5 >= 0 and i-5 < strip.numPixels():
            strip.setPixelColor(i-5,Color(8,0,0))
        if i-6 >= 0 and i-6 < strip.numPixels():
            strip.setPixelColor(i-6, Color(4,0,0))
        if i-7 >= 0 and i-7 < strip.numPixels():
            strip.setPixelColor(i-7,Color(2,0,0))
        if i-8 >= 0 and i-8 < strip.numPixels():
            strip.setPixelColor(i-8,Color(1,0,0))
       	if i-9 >= 0 and i-9 < strip.numPixels():
            strip.setPixelColor(i-9,0)
        if i+width-1 < strip.numPixels():
            strip.setPixelColor(i+width-1, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
    strip.setPixelColor(strip.numPixels()-1, 0)
    strip.show()
    light = light-1


def main():
    print'main started'
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    strip.begin()
    logging.basicConfig(filename='stairs.log', level=logging.INFO, format='%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s')
    logging.info('start scanning')
    first_pir = MotionSensor(4)
    second_pir = MotionSensor(17)
    print'starting socket'
    while True:
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect((HOST,PORT))
            break
        except socket.error,e:
            print str(e)
            time.sleep(2)
    output = None
    thread.start_new_thread( slow_light, (strip, Color(0,255,0)))
    if DEBUG:
        output = open(name='stairs.csv', mode='w', buffering=0)
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['timestamp'])
    else:
        db = Database()
    try:
        no_motion = True
        while True:
            if first_pir.motion_detected:
                if no_motion:
                    no_motion=False
                    timestamp = int(datetime.now().strftime('%s')) * 1000
                    if second_pir.motion_detected:
                        continue
                    else:
                        payload = "|".join([str(timestamp), '1', type])
                        try:
                            s.send(payload)
                            print'payload sent'
                        except socket.error:
                            print'host not reachable, saving locally'
                            db.save_entry(timestamp, 1)
                    time.sleep(.2)
                   # if DEBUG:
                   #     writer.writerow([timestamp])
                   # else:
                   #     db.save_entry(timestamp, 1)
                    if LIGHT:
                        thread.start_new_thread( running_light, (strip, Color(255, 0, 0)))
                no_motion=False
            else:
                no_motion = True
            time.sleep(.1)
    except KeyboardInterrupt:
        logging.info('closing scanner...')
        if output:
            output.close()


if __name__ == '__main__':
    main()
