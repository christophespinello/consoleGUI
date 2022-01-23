#!/usr/bin/python3

import serial
import threading
import queue 
import configparser

INIFILENAME = './consoleGUI.ini'

DEBUG_NO_COMM = False

ERR_IHK_SERIAL_OK = 0
ERR_IHK_SERIAL_NO_FRAME = -1

class SerialThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

        config = configparser.ConfigParser()
        config.read(INIFILENAME)

#        self.config = load_config(CONFIG_FILENAME)
        self.port = config['consoleGUI']['comport']
        self.debit = int(config['consoleGUI']['baudrate'])
        self.debug = False
        if (config['consoleGUI']['debug'] == 'true'):
            self.debug = True
        if not DEBUG_NO_COMM :
            self.serialPort = serial.Serial(self.port,self.debit)
        self.frame_type = config['consoleGUI']['frame_type']
        
    def save_configuration(self) :
#        self.config['debug'] = False
#        if (self.debug) :
#            self.config['debug'] = True
#        save_config(self.config, CONFIG_FILENAME)
        return("Configuration saved")
        

    def run(self):
#        self.serialPort.write(str.encode('help\n'))
#        time.sleep(0.2)
        test_end_frame = False
        s = ''
        while True:
            if not DEBUG_NO_COMM :
                if self.serialPort.inWaiting():
    #                text = self.serialPort.readline(self.serialPort.inWaiting())
                    try:
                        s = s + self.serialPort.readline(self.serialPort.inWaiting()).decode("utf-8")
                    except :
                        print("Error reading Line\n")
                        continue
                    if (self.frame_type == 'SUEZ') :
                        if (s[-1] == '\n') :
                            s = s.replace("\r\n","\n")
                            test_end_frame = True
                    if (self.frame_type == 'ZEHNDER') :
                        if (s[-1] == '\r') :
                            s = s.replace("\r","\r\n")
                            test_end_frame = True
                    if (test_end_frame == True) :
                        self.queue.put(s)
                        test_end_frame = False
                        s = ''
    def send_frame(self, s):
        if not DEBUG_NO_COMM :
            if (self.frame_type == 'SUEZ') :
                self.serialPort.write(str.encode(s + "\r\n"))
            if (self.frame_type == 'ZEHNDER') :
                self.serialPort.write(str.encode(s + "\n\r"))
    
    def close(self) :    
        self.serialPort.close()
