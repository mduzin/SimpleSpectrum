import wave
import struct
import math
import numpy as np
#import matplotlib.pyplot as plt
import time
import spidev
import RPi.GPIO as GPIO
 
 
#Zmienne globalne i Nastawy
SPI_CTX = {}  #zmienna z danymi do obslugi SPI
FileName = "WaveTest.wav"
#FileName = "test1.wav"
#FileName = "test4.wav"
FPS = 16   #FPS-ilosc klatek na sekunde 
N=8  #N - ilosc kolumn na wykresie spectrum   

#zmienne pomocnicze
BAR_ARRAY = np.fliplr(np.tril(np.ones((9,8),dtype=np.int),-1))

def PrepareBargraph(Spectrum):
    Result = np.vstack((BAR_ARRAY[item] for item in Spectrum))
    Result = np.packbits(Result, axis=0).flatten()
    return Result 

def DivideList(Spectrum,N):
    #metoda na przyspieszenie, pod warunkiem ze szerokosci przedzialow beda takie same
    Spectrum = np.reshape(Spectrum,(N,Spectrum.size/N))
    return np.amax(Spectrum, axis=1)  

def ScaleSpectrum(Spectrum,OldMax,NewMax):
    #Saturation filter
    SatSpectrum = np.clip(Spectrum,0,OldMax)
    #Scale array
    ScaleSpectrum = np.array(SatSpectrum)
    return np.around((ScaleSpectrum*NewMax)/OldMax)
 
#Zapis do MAX7219
def Max7219Write(spi_ctx,address,data):
    GPIO.output(spi_ctx['cs_pin'], GPIO.LOW)
    spi_ctx['dev'].xfer2([address, data])
    GPIO.output(spi_ctx['cs_pin'], GPIO.HIGH)
    return

 
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
#SPI_MOSI = 19
#SPI_CLK = 23
SPI_CS = 24    #nie wiem czemu ale w przykladzie bylo 23???

 
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
Max7219Write(SPI_CTX,REG_INTENSITY,2)
time.sleep(0.1)
 
#MAX7219 CLEAN
for i in range(MAX7219_ROW):
    Max7219Write(SPI_CTX,REG_DIGIT0 + i,0)
 
#MAX7219 TEST
#for i in range(MAX7219_ROW):
#    Max7219Write(SPI_CTX,REG_DIGIT0 + i,1<<i)
 

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
 

#FramesLength - number of frames we need to calculate current spectrum, eqaul to sampling frequency
#FramesShift  - number of frames over which we will shift our signal in single iteration (half of WindowLength)
#WaveData     - array of frame tuples from .wav file

#Chcemy żeby ilosc probek branych do liczenie widma byla wielokrotnoscia
#liczbt linii na wykresie
Mod_N = WaveParams.framerate%N
FramesLength = WaveParams.framerate - Mod_N
FramesShift  = math.floor(WaveParams.framerate/FPS)
WaveData    = []
WaveChannel = []
Spectrum    = []
 
for item in range(WaveParams.nchannels):
    WaveChannel.append([0]*FramesLength)
    Spectrum.append([])
    
 
i=0
while True:
    WaveFrame = WaveObj.readframes(FramesShift)
    if not WaveFrame: break
    BarSpectrum = []
    RealFramesLength = len(WaveFrame)//(WaveParams.sampwidth*WaveParams.nchannels)
    WaveFrame = struct.unpack('<{n}{t}'.format(n=RealFramesLength*WaveParams.nchannels,t=FormatDict[WaveParams.sampwidth]),WaveFrame)
 
    for n in range(WaveParams.nchannels):
        #isolate each channel 
        WaveChannel[n] = WaveChannel[n][RealFramesLength:]
        WaveChannel[n].extend([sample for (index,sample) in enumerate(WaveFrame) if (n == (index%WaveParams.nchannels))])
 
        #compute FFT for each channel
        WaveChannelLen = len(WaveChannel[n])
        Spectrum[n] = (2/WaveChannelLen)*np.fft.rfft(WaveChannel[n])
        Spectrum[n] = Spectrum[n][:-1]
        Spectrum[n] = abs(Spectrum[n])
 
        #teraz dzielimy nasze spectrum na N przedzialow
        #N - ilosc przedzialow
        #BarRange - ilosc prazakow czestotliwosci przypadajacych na pojedynczy przedzial
       
        BarSpectrum.append(DivideList(Spectrum[n],N))
        BarSpectrum[n] = ScaleSpectrum(np.array(BarSpectrum[n]),1000,8)
        
 
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
    #print("RealFramesLength: ", RealFramesLength )
    #print("len(WaveChannel[0]): ",len(WaveChannel[0]))
    #print("BarSpectrum[0]): ",BarSpectrum[0])
    Bargraph = PrepareBargraph(BarSpectrum[0])
    for x in range(MAX7219_ROW):
        Max7219Write(SPI_CTX,REG_DIGIT0+x,int(Bargraph[x]))
    i += 1
    #break

 
    
  
print("Koniec czytania pliku .wav")
#End of script
GPIO.cleanup()
print("Koniec skryptu")