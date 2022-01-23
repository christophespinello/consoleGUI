#!/usr/bin/python3

import serial
import threading
import queue 
import configparser
import logging

INIFILENAME = './IHKcli.ini'
_logging = logging.getLogger(__name__)

class IHKcliThread(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

        config = configparser.ConfigParser()
        config.read(INIFILENAME)

        self.port = config['IHKcli']['comport']
        self.debit = int(config['IHKcli']['baudrate'])
        self.serialPort = serial.Serial(self.port,self.debit)
        self.json_file = config['IHKcli']['json_filename']
        
    def run(self):
        test_end_frame = False
        s = ''
        while True:
            if self.serialPort.inWaiting():
                try:
                    s = s + self.serialPort.readline(self.serialPort.inWaiting()).decode('utf-8')
                except :
                    _logging.info('Error reading Line\n')
                    continue

                if (s[-1] == '\r') :
                    s = s.replace("\r","\r\n")
                    test_end_frame = True

                if (test_end_frame == True) :
                    self.queue.put(s)
                    test_end_frame = False
                    s = ''

    def send_frame(self, s):
        self.serialPort.write(str.encode(s + "\n\r"))
    
    def close(self) :    
        self.serialPort.close()
