#!/usr/bin/python3

import serial
import threading
import queue 
import configparser
import logging

import WRPnfcFrame

INIFILENAME = './WRPnfc.ini'

_logging = logging.getLogger(__name__)

class WRPnfcThread(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

        config = configparser.ConfigParser()
        config.read(INIFILENAME)

        self.port = config['WRPnfc']['comport']
        self.debit = int(config['WRPnfc']['baudrate'])
        self.json_file = config['WRPnfc']['json_filename']
        self.kmob = config['WRPnfc']['kmob']
        self.serialPort = serial.Serial(self.port,self.debit)
        
        self.EUID = 0
        self.counter = 0
        
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

                if (s[-1] == '\n') :
                    s = s.replace("\r\n","\n")
                    test_end_frame = True

                if (test_end_frame == True) :
                    self.queue.put(s)
                    test_end_frame = False
                    s = ''

    def send_frame(self, s):
        self.EUID = self.getEUID()
        
        s_split = s.split(' ')
        if (s_split[0] == 'send_nfc_command') :
            if (len(s_split) == 3) :
                frame = generateNFCframe(self.EUID, self.counter, s_split[1], s_split[2], self.kmob )
            else :
                _loggin.error('send_nfc_command bad number of arguments')
                return
            
        if (s_split[0] == 'send_nfc_7f_command') :
            if (len(s_split) == 2) :
                frame = generateNFCframe(self.EUID, self.counter, 0x7f, s_split[1], self.kmob )
            else :
                _loggin.error('senf_nfc_7f_command bad number of arguments')
                return
        
        self.serialPort.write(frame)
    
    def close(self) :    
        self.serialPort.close()
        
    def getEUID(self):
        self.serialPort.write('get_euid\n')
        answer = self.serialPort.readline()
        analyse_answer = answer.split(':')
        if (analyse_answer[0] == 'EUID') :
            return(analyse_answer[1][0:-1])