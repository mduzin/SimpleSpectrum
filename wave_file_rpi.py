import wave
import struct
import math
import numpy as np
#import matplotlib.pyplot as plt
import time
import spidev
import RPi.GPIO as GPIO
 
 
#Zmienne globalne i Nastawy

#zmienna z danymi do obslugi SPI
SPI_CTX = {}  

#Plik do analizy
#FileName = "yeah.wav"
#FileName = "test6.wav"
FileName = "vega.wav"

#Ilosc klatek na sek do wyswietlenia
FPS = 16   #FPS-ilosc klatek na sekunde 

#N - ilosc kolumn na wykresie spectrum 
N = 8    

#H - wyskosc slupka kolumny
H = 8

#Tablica z wyliczonymi widmami do wyswietlenia
BarArray = []

#zmienne pomocnicze
BAR_ARRAY = np.fliplr(np.tril(np.ones((H+1,H),dtype=np.int),-1))

#<TODO:> komentarz
def PrepareBargraph(Spectrum):
    Result = np.vstack((BAR_ARRAY[item] for item in Spectrum))
    Result = np.packbits(Result, axis=0).flatten()
    return Result 

#<TODO:> komentarz    
def DivideList(Spectrum,N):
    #metoda na przyspieszenie, pod warunkiem ze szerokosci przedzialow beda takie same
    Spectrum = np.reshape(Spectrum,(N,Spectrum.size/N))
    return np.amax(Spectrum, axis=1)  

#<TODO:> komentarz    
def ScaleSpectrum(Spectrum,OldMax,NewMax):
    #Saturation filter
    SatSpectrum = np.clip(Spectrum,0,OldMax)
    #Scale array
    ScaleSpectrum = np.array(SatSpectrum)
    return np.around((ScaleSpectrum*NewMax)/OldMax)
 
#Zapis do MAX7219
#IN spi_ctx - handle do contextu polaczenia spi
#IN address - adres rejestru max7219 do ktorego bedziemy pisac
#IN data    - dane wysylane do rejestru
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
SPI_MOSI = 19
SPI_CLK = 23
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
#WaveData     - array of frames from .wav file

#Chcemy żeby ilosc probek branych do liczenie widma byla wielokrotnoscia ilosci linii na wykresie
FramesLength = WaveParams.framerate - WaveParams.framerate%N
FramesShift  = math.floor(WaveParams.framerate/FPS)
WaveData     = np.zeros(FramesLength)
    
 
i=0
while True:
    #pobieramy nowe ramki z pliku
    WaveFrame = WaveObj.readframes(FramesShift)
    
    #jesli nie ma wiecej ramek to wyjdz z petli
    if not WaveFrame: break

    #Flow:
    #1. stworz macierz numpy na ramki (inicuj zerami) DONE 
    #2. odczyt nowej porcji danych tak jak jest: WaveFrame = WaveObj.readframes(FramesShift)DONE
    #3. usun przestarzale ramki z poczatku .delete DONE
    #4. dodanie odczytanej macierzy numpy z ramkami .append DONE
    #5. rozdzial na kanalay .reshape DONE
    #6. obliczanie rfft DONE
    RealFramesLength = len(WaveFrame)//(WaveParams.sampwidth*WaveParams.nchannels)
    WaveFrame = struct.unpack('<{n}{t}'.format(n=RealFramesLength*WaveParams.nchannels,t=FormatDict[WaveParams.sampwidth]),WaveFrame)
    WaveData = np.delete(WaveData, np.s_[0:len(WaveFrame)], None)    
    WaveData = np.append(WaveData,WaveFrame)
    WaveChannel = np.array(WaveData).reshape(-1,WaveParams.nchannels)
    
    
    #liczymy rfft tylko wszystkich kanalow
    Spectrum = np.absolute(np.fft.rfft(WaveChannel,axis=0))
    #nie wiem po co było to usuwanie ostatniego elementu(po nic tylko po to by ilosc ramek sie ladnie dzielila)
    # ja usuwam pierwsza probke czyli 0Hz
    Spectrum = np.sum(np.delete(Spectrum, 0, 0),axis=1)
   
    
    #teraz dzielimy nasze spectrum na N przedzialow
    #N - ilosc przedzialow
          
    Spectrum = DivideList(Spectrum,N)
    #<TODO:> Obmyslec lepszy sposob skalowania max'a
    Spectrum = ScaleSpectrum(Spectrum,100,H)
    Bargraph = PrepareBargraph(Spectrum)
   
    for x in range(MAX7219_ROW):
        Max7219Write(SPI_CTX,REG_DIGIT0+x,int(Bargraph[x]))
       
 
    print("Iter: ",i)
    #print("Spectrum: ",Spectrum)
    i += 1
    #break

 
    
  
print("Koniec czytania pliku .wav")

#End of script
GPIO.cleanup()
print("Koniec skryptu")