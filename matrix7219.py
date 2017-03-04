# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 15:30:48 2017

@author: M
"""

#Module to operate with max7219 serially connected devices
import time
import spidev
import numpy as np
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
#SPI CTX INIT
SPI_CTX['dev'] = spidev.SpiDev()
SPI_CTX['dev'].open(0, 0)
SPI_CTX['dev'].mode = 3
SPI_CTX['dev'].max_speed_hz = 1000000
SPI_CTX['cs_pin'] = SPI_CS


#Zapis do MAX7219
#IN address - adres rejestru max7219 do ktorego bedziemy pisac
#IN data    - dane wysylane do rejestru
def Max7219Write(address,data):
    GPIO.output(SPI_CTX['cs_pin'], GPIO.LOW)
    SPI_CTX['dev'].xfer2([address, data])
    GPIO.output(SPI_CTX['cs_pin'], GPIO.HIGH)
    return

#Zapis do Matrix max7219
#IN data_arr - dane do wyslania do matrixa, musza miec 
#odpowiedni format i dlugosc w formacie: 
#data_arr = [addr1,data1,adddr2,data2,addr3,data3...] 
#ilosc sekwencji addrX,dataX musi byc rowna ilosci wyswietlaczy 'n'
def Matrix7219Write(data_arr):
    GPIO.output(SPI_CTX['cs_pin'], GPIO.LOW)
    SPI_CTX['dev'].xfer2(data_arr)
    GPIO.output(SPI_CTX['cs_pin'], GPIO.HIGH)
    return    
     
    
#inicjalizacja GPIO na Rpi
def InitGpio():
    #GPIO INIT
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SPI_CS, GPIO.OUT)
    GPIO.output(SPI_CS, GPIO.HIGH)
    time.sleep(0.1)

    
#Get currently displayed matrix values    
def Matrix7219GetMatrixData(matrix_7219_ctx):
    return matrix_7219_ctx['Data']


#Send matrix values to be displayed
#data shall have format:
#int array [[addr0,data00,addr0,data01,addr0,data02...,addr0,data0n],
#           [addr1,data10,addr1,data11,addr1,data12...,addr1,data1n],
#                 ...
#           [addrH,dataH0,addrH,dataH1,addrH,dataH2...,addrH,dataHn]] 
def Matrix7219SendMatrixData(matrix_7219_ctx,data):
    #if format danych sie zgada z aktualna konfiguracja wyswietlaczy
    if data.shape == (matrix_7219_ctx['H'],matrix_7219_ctx['n']*2):
        diffData = matrix_7219_ctx['Data'] - data
        if 0 != np.sum(diffData):
            for diff_row,row in zip(diffData,data):
                if 0 != sum(diff_row):
                    int_row = [int(x) for x in row]
                    Matrix7219Write(int_row)
        #store data as current displayed data
        matrix_7219_ctx['Data'] = data
    return    

#Get current matrix configuration
def Matrix7219GetMatrixConfig(matrix_7219_ctx):
    ...
    return 

#Send current matrix configuration    
def Matrix7219SendMatrixConfig(matrix_7219_ctx,config):
    ...
    return        

    
#Otwarcie liba do obslugi wyswietlaczy max7219 polaczonych
#szeregow. 
# IN n - ilosc wyswietlaczy polaczonych szeregowo
# IN H - ilosc wierszy w wyswietlaczu
# IN N - ilosc kolumn w wyswietlaczu
# OUT Matrix7219_handle - obiekt max7219 polaczonych szeregowo
def Matrix7219Open(n=2,H=8,N=8):
    MATRIX_7219_CTX = {}
    MATRIX_7219_CTX['n'] = n
    MATRIX_7219_CTX['N'] = N*n
    MATRIX_7219_CTX['H'] = H
    
    #zmienne pomocnicze
    MATRIX_7219_CTX['BAR_ARR'] = np.fliplr(np.tril(np.ones((H+1,H),dtype=np.int),-1))
    MATRIX_7219_CTX['REG_ARR'] = np.array([REG_DIGIT0,   
                                           REG_DIGIT1,
                                           REG_DIGIT2,
                                           REG_DIGIT3,
                                           REG_DIGIT4,
                                           REG_DIGIT5,
                                           REG_DIGIT6,
                                           REG_DIGIT7,]*n).reshape(n,8).transpose()    
    MATRIX_7219_CTX['Data'] = np.zeros((H,n*2), dtype=int)
    
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
        Matrix7219Write(item*matrix_7219_ctx['n'])
    time.sleep(0.1)
    return
    
    
#Matrix max7219 clean up
def Matrix7219Clean(matrix_7219_ctx):
    matrix_7219_ctx['Data']
    for i in range(MAX7219_ROW):
        Matrix7219Write([REG_DIGIT0 + i,0]*matrix_7219_ctx['n'])
    return
    
    
def Matrix7219Close(): 
    GPIO.cleanup()
    return
    
#script simple unittest
if __name__ == "__main__":
    MATRIX_CTX = Matrix7219Open(n=2)
    Matrix7219Init(MATRIX_CTX)
    Matrix7219Clean(MATRIX_CTX)
    
    #prepare test data to display
    for item in range(256):
        DisplayData = np.ones((MATRIX_CTX['H'],MATRIX_CTX['n']), dtype=int)*item
        DisplayData = np.insert(DisplayData,np.arange(MATRIX_CTX['n']),MATRIX_CTX['REG_ARR'],axis=1)
        Matrix7219SendMatrixData(MATRIX_CTX,DisplayData)
        time.sleep(0.2)
    
    Matrix7219Clean(MATRIX_CTX)
    Matrix7219Close()
    
    