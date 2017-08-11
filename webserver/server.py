import socket
import sqlite3
import os
import time

DEBUG = False

class Database(object):
    '''
    database class using sqlite3
    '''
    def __init__(self):
        self.db = 'actistairs.db'
        cnx = sqlite3.connect(self.db)
        cursor = cnx.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS entry (timestamp INTEGER NOT NULL, count INTEGER NOT NULL, type VARCHAR(250) NOT NULL, PRIMARY KEY (timestamp), UNIQUE(timestamp))''')
        cnx.commit()
        cnx.close()
    
    def save_entry(self, timestamp, count, type):
        '''
        Save the given entry
        '''
        print 'saving in db'
        cnx = sqlite3.connect(self.db)
        cursor = cnx.cursor()
        print'got cursor'
        cursor.execute('INSERT OR IGNORE INTO entry VALUES (?, ?, ?)', [timestamp, count, type])
        print'query done'
        cnx.commit()
        print'saved'
                   
HOST='169.254.214.44'
PORT = 2003
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
db=Database()
print'socket created'

while True:
    try:
        s.bind((HOST,PORT))
        print'socket bound'
        break
    except socket.error,e:
        print str(e) +  'waiting for network'
        time.sleep(1)        
    
s.listen(5)
print'Socket waiting for messages'
(conn,addr)=s.accept()
print'Connected'

while True:
    try:
        data = conn.recv(1024)
        print 'got params'
        params = data.split('|')
        print 'data converted'
        print int(params[0]), int(params[1]), params[2]
        db.save_entry(int(params[0]), int(params[1]), params[2])
        conn.send('Done')
    except socket.error:
        print'Lost connection'
        #os.system('sudo reboot')
        break
                   
