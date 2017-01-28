# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 15:30:48 2017

@author: M
"""

#Module to operate with max7219 serially connected devices
import time
import spidev
import RPi.GPIO as GPIO

 
#Adresy rejestrow MAX7219
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
SPI_MOSI = 19
SPI_CLK  = 23
SPI_CS   = 24    #nie wiem czemu ale w przykladzie bylo 23???

#zmienna z danymi do obslugi SPI
SPI_CTX = {}  

#Zapis do MAX7219
#IN spi_ctx - handle do contextu polaczenia spi
#IN address - adres rejestru max7219 do ktorego bedziemy pisac
#IN data    - dane wysylane do rejestru
def Max7219Write(spi_ctx,address,data):
    GPIO.output(spi_ctx['cs_pin'], GPIO.LOW)
    spi_ctx['dev'].xfer2([address, data])
    GPIO.output(spi_ctx['cs_pin'], GPIO.HIGH)
    return

#Zapis do Matrix max7219
#IN spi_ctx - handle do contextu polaczenia spi
#IN data_arr - dane do wyslania do matrixa, musza miec 
#odpowiedni format i dlugosc w formacie: 
#data_arr = [addr1,data1,adddr2,data2,addr3,data3...] 
#ilosc sekwencji addrX,dataX musi byc rowna ilosci wyswietlaczy 'n'
def Matrix7219Write(spi_ctx,data_arr):
    GPIO.output(spi_ctx['cs_pin'], GPIO.LOW)
    spi_ctx['dev'].xfer2(data_arr)
    GPIO.output(spi_ctx['cs_pin'], GPIO.HIGH)
    return    
    
#<TODO:> wysylanie par danych z data_chain [addr,data] po kolei 
#do wszystkich modulow spietych szeregow
#nalezy dolozyc wpisy no_op na koncu
def Matrix7219WriteChain(spi_ctx,data_chain):
    return  
    
#inicjalizacja SPI na Rpi
def InitSpiCtx():
    #SPI CTX INIT
    SPI_CTX['dev'] = spidev.SpiDev()
    SPI_CTX['dev'].open(0, 0)
    SPI_CTX['dev'].mode = 3
    SPI_CTX['dev'].max_speed_hz = 1000000
    SPI_CTX['cs_pin'] = SPI_CS
    time.sleep(0.1)
    return
#inicjalizacja GPIO na Rpi
def InitGpio():
    #GPIO INIT
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SPI_CS, GPIO.OUT)
    GPIO.output(SPI_CS, GPIO.HIGH)
    time.sleep(0.1)

#Otwarcie liba do obslugi wyswietlaczy max7219 polaczonych
#szeregow. 
# IN n - ilosc wyswietlaczy polaczonych szeregowo
# OUT Matrix7219_handle - obiekt max7219 polaczonych szeregowo
def Matrix7219Open(n=2):
    MATRIX_7219_CTX = {}
    MATRIX_7219_CTX['n'] = n
    InitSpiCtx()
    InitGpio()
    return MATRIX_7219_CTX

#inicjalizacja wyswietlaczy 7219 polaczonych szeregowo    
def Matrix7219Init(matrix_7219_ctx):
    InitValues = [[REG_DECODEMODE,0],
                  [REG_SCANLIMIT, 7],
                  [REG_DISPLAYTEST,0],
                  [REG_SHUTDOWN,1],
                  [REG_INTENSITY,2]]
    for item in InitValues:
        Matrix7219Write(SPI_CTX,item*matrix_7219_ctx['n'])
    time.sleep(0.1)
    return
    
    
#Matrix max7219 clean up
def Matrix7219Clean(matrix_7219_ctx):
    for i in range(MAX7219_ROW):
        Matrix7219Write(SPI_CTX,[REG_DIGIT0 + i,0]*matrix_7219_ctx['n'])
    return
    
    
def Matrix7219Close(): 
    GPIO.cleanup()
    return
    
    
    
    