# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 19:27:11 2016

@author: M
"""

#!/usr/bin/env python
 
import time
import spidev
import RPi.GPIO as GPIO
 
#Adresy rejestrow
NO_OP           = 0x0
REG_DIGIT0      = 0x1
REG_DIGIT1      = 0x2
REG_DIGIT2      = 0x3
REG_DIGIT3      = 0x4
REG_DIGIT4      = 0x5
REG_DIGIT5      = 0x6
REG_DIGIT6      = 0x7
REG_DIGIT7      = 0x8
REG_DECODEMODE  = 0x9
REG_INTENSITY   = 0xA
REG_SCANLIMIT   = 0xB
REG_SHUTDOWN    = 0xC
REG_DISPLAYTEST = 0xF
 
#ilosc ukladow w kaskadzie
MAX7219_COUNT = 2
MAX7219_ROW   = 8
MAX7219_COL   = 8
 
#Numery pinow SPI
#SPI_MOSI = 19
#SPI_CLK = 23
SPI_CS = 24    #nie wiem czemu ale w przykladzie bylo 23???
 
 
#zmienna z danymi do obslugi SPI
SPI_CTX = {}
 
 
#musze to lepiej przemyslec
def Max7219Write(spi_ctx,address,data):
    GPIO.output(spi_ctx['cs_pin'], GPIO.LOW)
    spi_ctx['dev'].xfer2([address, data])
    GPIO.output(spi_ctx['cs_pin'], GPIO.HIGH)
    return
 
#GPIO INIT
GPIO.setmode(GPIO.BCM)
GPIO.setup(SPI_CS, GPIO.OUT)
GPIO.output(SPI_CS, GPIO.HIGH)
time.sleep(0.1)
 
#SPI CTX INIT
SPI_CTX['dev'] = spidev.SpiDev()
SPI_CTX['dev'].open(0, 0)
SPI_CTX['dev'].mode = 3
SPI_CTX['dev'].max_speed_hz = 1000000
SPI_CTX['cs_pin'] = SPI_CS
time.sleep(0.1)
 
#MAX7219 INIT
#<TODO:> Pamietaj ze mamy dwa wyswietlacze
Max7219Write(SPI_CTX,REG_DECODEMODE,0)
Max7219Write(SPI_CTX,REG_SCANLIMIT, 7)
Max7219Write(SPI_CTX,REG_DISPLAYTEST,0)
Max7219Write(SPI_CTX,REG_SHUTDOWN,1)
Max7219Write(SPI_CTX,REG_INTENSITY,1)
time.sleep(0.1)
 
#MAX7219 CLEAN
for i in range(MAX7219_ROW):
    Max7219Write(SPI_CTX,REG_DIGIT0 + i,0)
 
#MAX7219 TEST
#for i in range(MAX7219_ROW):
#    Max7219Write(SPI_CTX,REG_DIGIT0 + i,1<<i)
 
#End of script
GPIO.cleanup()
print("Koniec skryptu")