# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 15:30:48 2017

@author: M
"""

#Library module
#API for display bargraphs on [n] serially connected max7219
#example hardware: http://www.waveshare.com/rpi-led-matrix.htm

import time
import spidev
import numpy as np
import RPi.GPIO as GPIO

#MAX7219 registers address
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

#SPI pin numbers
SPI_MOSI = 19
SPI_CLK  = 23
SPI_CS   = 24

#SPI interface context
SPI_CTX = {}  

#Write to MAX7219 procedure
#IN address - MAX7219 register address
#IN data    - data send to register
def Max7219Write(address,data):
    GPIO.output(SPI_CTX['cs_pin'], GPIO.LOW)
    SPI_CTX['dev'].xfer2([address, data])
    GPIO.output(SPI_CTX['cs_pin'], GPIO.HIGH)
    return

#Write to Matrix MAX7219
#IN data_arr - data array for matrix max7219
#Data_arr format:
#data_arr = [addr1,data1,adddr2,data2,addr3,data3...]
#number od pairs addrX,dataX should equals number of connected MAX7219
def Matrix7219Write(data_arr):
    GPIO.output(SPI_CTX['cs_pin'], GPIO.LOW)
    SPI_CTX['dev'].xfer2(data_arr)
    GPIO.output(SPI_CTX['cs_pin'], GPIO.HIGH)
    return

#Rpi GPIO init procedure
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
    if data.shape == (matrix_7219_ctx['H'],matrix_7219_ctx['n']*2):
        diffData = matrix_7219_ctx['Data'] - data
        if 0 != np.sum(diffData):
            for diff_row,row in zip(diffData,data):
                if 0 != sum(diff_row):
                    int_row = [int(x) for x in row]
                    Matrix7219Write(int_row)
#                else:
#                    print("Row without changes")
            #store data as current displayed data
            matrix_7219_ctx['Data'] = data
#        else:
#            print("Data without changes")
#    else:
#        print("Wrong data shape")
    return

#Get current matrix configuration
def Matrix7219GetMatrixConfig(matrix_7219_ctx):
    ...
    return

#Send current matrix configuration    
def Matrix7219SendMatrixConfig(matrix_7219_ctx,config):
    ...
    return

#Create Matrix MAX7219 object
# IN n - number od serially connected MAX7219
# IN H - row number in single MAX7219
# IN N - col number in single MAX7219
# OUT Matrix7219_handle - martrix7219 object
def Matrix7219Open(n=2,H=8,N=8):
    #SPI CTX INIT
    SPI_CTX['dev'] = spidev.SpiDev()
    SPI_CTX['dev'].open(0, 0)
    SPI_CTX['dev'].mode = 3
    SPI_CTX['dev'].max_speed_hz = 1000000
    SPI_CTX['cs_pin'] = SPI_CS
    
    MATRIX_7219_CTX = {}
    MATRIX_7219_CTX['n'] = n
    MATRIX_7219_CTX['N'] = N*n
    MATRIX_7219_CTX['H'] = H

    #additional variables
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
    
    #configure GPIO pin
    InitGpio()
    return MATRIX_7219_CTX

#MAX7219 modules nitialization
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

#Matrix MAX7219 clean up
def Matrix7219Clean(matrix_7219_ctx):
    matrix_7219_ctx['Data']
    for i in range(matrix_7219_ctx['H']):
        Matrix7219Write([REG_DIGIT0 + i,0]*matrix_7219_ctx['n'])
    return

#Matrix MAX7219 close
def Matrix7219Close():
    GPIO.cleanup()
    SPI_CTX['dev'].close()
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
