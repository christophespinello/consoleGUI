#!/usr/bin/python3

from Crypto.Hash import CMAC
from Crypto.Cipher import AES
import Crypto.Util.Counter

from binascii import unhexlify, hexlify
from Crypto.Util.Padding import pad

import crcmod

import hmac
import hashlib
import base64
import crcmod

def generateNFCframe(EUID, compteur, cField, frame, kmob_key):

    Ack = '00'

    iv = EUID + compteur + '000000000000'

    Kmob_Bytes = unhexlify(kmob_key)
    frame_Bytes = unhexlify(frame)
    IV_Bytes = unhexlify(iv)

    ciphered_frame = ''
    
    if (frame != '') :
        ctr=Crypto.Util.Counter.new(128, initial_value=int(iv,16))
        cipher = AES.new(Kmob_Bytes, AES.MODE_CTR, counter=ctr)
        ciphered_data = cipher.encrypt(frame_Bytes)
        ciphered_frame = format(int(hexlify(ciphered_data),16),'0256X')
        ciphered_frame = ciphered_frame[-len(frame):]
    
    msg = compteur + cField + Ack + ciphered_frame
    LField = format(int(len(msg)/2)+4,'02X')
    msg = LField + msg
    msg = EUID + msg
    msg_Bytes = unhexlify(msg)
    
    obj = CMAC.new(Kmob_Bytes,ciphermod = AES)
    signature = format(int(obj.update(msg_Bytes).hexdigest()[0:8],16),'08X')
    
    output_frame = LField + compteur + cField + Ack + ciphered_frame + signature
    
    crc16 = crcmod.mkCrcFun(0x13D65, rev=False, initCrc=0x0000, xorOut=0x0000)
    crc = format(crc16(unhexlify(output_frame)) ^ 0xFFFF,'04X')
    
    output_frame += crc
    
    return(output_frame)

def decryptNFCframe(EUID, frame, kmob_key):

# Verification du champs L
    msg_Bytes = unhexlify(frame)
    if (msg_Bytes[0] != len(msg_Bytes)-3) :
        return('LField Error')

# Verification du CRC
    crc16 = crcmod.mkCrcFun(0x13D65, rev=False, initCrc=0x0000, xorOut=0x0000)
    crc = format(crc16(unhexlify(frame[0:-4])) ^ 0xFFFF,'04X')

    if (crc != frame[-4:]) :
        return('CRC error')
    
    frame = frame[0:-4]

    Kmob_Bytes = unhexlify(kmob_key)
    msg = EUID + frame[0:-8]
    msg_Bytes = unhexlify(msg)

    obj = CMAC.new(Kmob_Bytes,ciphermod = AES)
    signature = format(int(obj.update(msg_Bytes).hexdigest()[0:8],16),'08X')
    
    if (signature != frame[-8:]) :
        return('HashKMOB error')

    frame = frame[0:-8]

    Lfield = int(frame[0:2],16)
    cptField = int(frame[2:6],16)
    Cfield = int(frame[6:8],16)
    ackField = int(frame[8:10],16)

    iv = EUID + format(cptField,'04X') + '000000000000'

    Kmob_Bytes = unhexlify(kmob_key)
    frame_Bytes = unhexlify(frame[10:])

    ciphered_frame = ''
    
    if (frame != '') :
        ctr=Crypto.Util.Counter.new(128, initial_value=int(iv,16))
        cipher = AES.new(Kmob_Bytes, AES.MODE_CTR, counter=ctr)
        ciphered_data = cipher.encrypt(frame_Bytes)
        ciphered_frame = format(int(hexlify(ciphered_data),16),'0256X')
        ciphered_frame = ciphered_frame[-len(frame[10:]):]

    return(ciphered_frame)
    
#    msg = compteur + cField + Ack + ciphered_frame
#    LField = format(int(len(msg)/2)+4,'02X')
#    msg = LField + msg
#    msg = EUID + msg
#    msg_Bytes = unhexlify(msg)
    
#    obj = CMAC.new(Kmob_Bytes,ciphermod = AES)
#    signature = format(int(obj.update(msg_Bytes).hexdigest()[0:8],16),'08X')
    
#    output_frame = LField + compteur + cField + Ack + ciphered_frame + signature
    
#    crc16 = crcmod.mkCrcFun(0x13D65, rev=False, initCrc=0x0000, xorOut=0x0000)
#    crc = format(crc16(unhexlify(output_frame)) ^ 0xFFFF,'04X')
    
#    output_frame += crc
    
#    return(output_frame)


Kmac = '715AD8835BC95470260BA34092A87398'
Kenc = 'F1136B5BD0F8A6D88375B7948F8A763A'
#Kmob = '83CB3D3FDCA09194A56C6D4DBDA3C535'
Kmob = '6B424ECC0B4C7764CECACC6A9A74F7F5'

Eeprom_EUID = 'E0022601D94A845C'
Eeprom_EUID = 'E0022601B2EF894D'
Eeprom_EUID = 'E0022601B2E45FD8'
Cnt = '0003'
CField = '01'
CField = '08'
CField = '7F'
Ack = '00'


Kmac_Bytes = unhexlify(Kmac)
Kenc_Bytes = unhexlify(Kenc)

Frame = '64F14B6A029D4EC3F5'
receivedFrame = '0E000AFF006CE9FE5CEFCA0511FE89F7D9'
#frame=''
#frame = '41542B52454144204D4F44450D0A'
#frame_Bytes = unhexlify(frame)
#print(frame_Bytes)

#print(generateNFCframe(Eeprom_EUID,Cnt,CField,Frame,Kmob))
print(decryptNFCframe(Eeprom_EUID,receivedFrame,Kmob))

input('pause')
