#!/usr/bin/python3

import serial
import threading
import queue 
import configparser
import logging

INIFILENAME = './WRPuart.ini'

_logging = logging.getLogger(__name__)

class WRPuartThread(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

        config = configparser.ConfigParser()
        config.read(INIFILENAME)

        self.port = config['WRPuart']['comport']
        self.debit = int(config['WRPuart']['baudrate'])
        self.json_file = config['IHKcli']['json_filename']
        self.serialPort = serial.Serial(self.port,self.debit)
        
    def run(self):
        test_end_frame = False
        s = ''
        while True:
            if not DEBUG_NO_COMM :
                if self.serialPort.inWaiting():
    #                text = self.serialPort.readline(self.serialPort.inWaiting())
                    try:
                        s = s + self.serialPort.readline(self.serialPort.inWaiting()).decode('utf-8')
                    except :
                        _logging.info('Error reading Line\n')
                        continue

                    if (s[-1] == '\n') :
                        s = s.replace("\r\n","\n")
                        test_end_frame = True

                    if (test_end_frame == True) :
                        self.queue.put(s)
                        test_end_frame = False
                        s = ''

    def send_frame(self, s):
        self.serialPort.write(str.encode(s + "\r\n"))
    
    def close(self) :    
        self.serialPort.close()
