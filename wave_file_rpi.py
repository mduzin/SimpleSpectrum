import wave
import struct
import math
import numpy as np
#import matplotlib.pyplot as plt
import time
import spidev
import RPi.GPIO as GPIO
 
 
def DivideList(Spectrum,N,aggr_func):
    
    #metoda na przyspieszenie, pod warunkiem ze szerokosci przedzialow beda takie same
    #if 0==(len(Spectrum)%N):
    #   return aggr_func(np.reshape(Spectrum,(N,len(Spectrum)/N)))
    
    BarRange = len(Spectrum)/N
    BarSpectrum = []
 
    #czy mozna jakos zoptymalizowac Start i Stop Index'u???
    StartIndex = 0.0
    StopIndex = StartIndex + BarRange
    for x in range(N):
        BarSpectrum.append(Spectrum[round(StartIndex):round(StopIndex)])
        StartIndex = StopIndex;
        StopIndex =  StartIndex + BarRange
 
    BarSpectrum = [aggr_func(x) for x in BarSpectrum]
    return BarSpectrum
    

OldRange = {'max':1000, 'min':0}
NewRange = {'max': 8, 'min':0}
def ScaleArray(Array):
    a = (NewRange['min']-NewRange['max'])/(OldRange['min']-OldRange['max'])
    b = NewRange['min'] - a*OldRange['min']

    NewArray = a*Array +b

    for i in range(len(NewArray)):
        if NewArray[i] > NewRange['max']:
            NewArray[i] = NewRange['max']
        if NewArray[i] < NewRange['min']:
            NewArray[i] = NewRange['min']
   
    return [int(i) for i in NewArray]
 


 
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
 

FileName = "WaveTest.wav"
#FileName = "test.wav"
#FileName = "test4.wav"
WaveObj = wave.open(FileName, mode='rb')
 
print("Channels: ".ljust(25),WaveObj.getnchannels())
print("Sample width: ".ljust(25),WaveObj.getsampwidth()," bytes")
print("Sampling frequency: ".ljust(25),WaveObj.getframerate()," Hz")
print("Number of audio frames: ".ljust(25),WaveObj.getnframes())
print("Compression type: ".ljust(25),WaveObj.getcomptype(),"\n")
 
WaveParams = WaveObj.getparams(); #print("Params: ".ljust(25),WaveParams, "\n")
 
#8-bit samples are stored as unsigned bytes, ranging from 0 to 255. 
#16-bit samples are stored as 2's-complement signed integers, ranging from -32768 to 32767.
#.wav file is always Little Endian so we use '<'
FormatDict = {1:'B',2:'h',4:'i',8:'q'}
 
#FPS          - ilosc klatek na sekunde 
#WindowLength - number of frames we need to calculate current spectrum, eqaul to sampling frequency
#WindowShift  - number of frames over which we will shift our signal in single iteration (half of WindowLength)
#WaveData     - array of frame tuples from .wav file
FPS = 16
WindowLength = WaveParams.framerate
WindowShift  = math.floor(WaveParams.framerate/FPS)
WaveData = []
WaveChannel = []
Spectrum = []
 
for item in range(WaveParams.nchannels):
    WaveChannel.append([0]*WindowLength)
    Spectrum.append([])
    
 
i=0
while True:
    WaveFrame = WaveObj.readframes(WindowShift)
    if not WaveFrame: break
    BarSpectrum = []
    RealFrameNum = len(WaveFrame)//(WaveParams.sampwidth*WaveParams.nchannels)
    WaveFrame = struct.unpack('<{n}{t}'.format(n=RealFrameNum*WaveParams.nchannels,t=FormatDict[WaveParams.sampwidth]),WaveFrame)
 
    for n in range(WaveParams.nchannels):
        #isolate each channel 
        WaveChannel[n] = WaveChannel[n][RealFrameNum:]
        WaveChannel[n].extend([sample for (index,sample) in enumerate(WaveFrame) if (n == (index%WaveParams.nchannels))])
 
        #compute FFT for each channel
        WaveChannelLen = len(WaveChannel[n])
        Spectrum[n] = (2/WaveChannelLen)*np.fft.fft(WaveChannel[n])
        Spectrum[n] = Spectrum[n][:math.floor(WaveChannelLen/2)]
        Spectrum[n] = abs(Spectrum[n])
 
        #teraz dzielimy nasze spectrum na N przedzialow
        #N - ilosc przedzialow
        #BarRange - ilosc prazakow czestotliwosci przypadajacych na pojedynczy przedzial
        N=8
        BarSpectrum.append(DivideList(Spectrum[n],N,max))
        BarSpectrum[n] = ScaleArray(np.array(BarSpectrum[n]))
        
 
    #rysuj/updatuj wykres widma
    #plt.figure(1)
    #plt.ylabel('Amplitude')
    #plt.xlabel('Czestoliwosc [Hz]')
    #plt.title('Widmo')
    #plt.ylim(0.0, 1000.0)
    #plt.plot(abs(Spectrum[0]),'r')
    #plt.bar(np.arange(N),BarSpectrum[0])
    #plt.grid(True)
    #plt.show()
 
    print("Iter: ",i)
    print("RealFrameNum: ",RealFrameNum )
    print("len(WaveChannel[0]): ",len(WaveChannel[0]))
    print("BarSpectrum[0]): ",BarSpectrum[0])
    for x in range(MAX7219_ROW):
        Max7219Write(SPI_CTX,REG_DIGIT0 + x,2**(BarSpectrum[0][x])-1)
    i += 1;

 
    
  
print("Koniec czytania pliku .wav")
#End of script
GPIO.cleanup()
print("Koniec skryptu")