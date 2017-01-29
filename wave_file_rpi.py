import wave
import struct
import math
import numpy as np
import matrix7219
 
 
#Zmienne globalne i Nastawy


#Plik do analizy
#FileName = "yeah.wav"
#FileName = "test6.wav"
FileName = "vega.wav"

#Ilosc klatek na sek do wyswietlenia
FPS = 23   #FPS-ilosc klatek na sekunde 

#N - ilosc kolumn na wykresie spectrum 
N = 16    

#H - wyskosc slupka kolumny
H = 8

#Tablica z wyliczonymi widmami do wyswietlenia
BarArray = []

#zmienne pomocnicze
BAR_ARRAY = np.fliplr(np.tril(np.ones((H+1,H),dtype=np.int),-1))

#<TODO:> komentarz
def PrepareBargraph(Spectrum,n=1):
    #wpierw musimy podzielic Spectrum na n wyswietlaczy
    Spectrum = Spectrum.reshape(n,-1) 
    Result = []
    for max7219bars in Spectrum:
        Bars = np.vstack((BAR_ARRAY[item] for item in max7219bars))
        Bars = np.packbits(Bars, axis=0).flatten()
        Result.append(Bars)
    return np.array(Result)

#Dzieli przeslana liste na N podlist, pod warunkiem że sa one podzielne przez N
def DivideList(Spectrum,N):
    #metoda na przyspieszenie, pod warunkiem ze szerokosci przedzialow beda takie same
    if 0==(Spectrum.size%N):
        Spectrum = np.reshape(Spectrum,(N,Spectrum.size//N))
        return np.amax(Spectrum, axis=1)  
  
        
#<TODO:> komentarz    
def ScaleSpectrum(Spectrum,OldMax,NewMax):
    #Saturation filter
    SatSpectrum = np.clip(Spectrum,0,OldMax)
    #Scale array
    ScaleSpectrum = np.array(SatSpectrum)
    return np.around((ScaleSpectrum*NewMax)/OldMax)
 

MATRIX_CTX = matrix7219.Matrix7219Open(n=2)
matrix7219.Matrix7219Init(MATRIX_CTX)
matrix7219.Matrix7219Clean(MATRIX_CTX)

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
    
    #liczymy rfft dla wszystkich kanalow
    Spectrum = np.absolute(np.fft.rfft(WaveChannel,axis=0))
    # ja usuwam pierwsza probke czyli 0Hz
    # oraz sumuje wszystkie kanaly
    Spectrum = np.sum(np.delete(Spectrum, 0, 0),axis=1)
    #przejscie na decybele
    Spectrum = np.log10(Spectrum)
    
    #teraz dzielimy nasze spectrum na N przedzialow
    #N - ilosc przedzialow
          
    Spectrum = DivideList(Spectrum,N)
    #<TODO:> Obmyslec lepszy sposob skalowania max'a
    #Spectrum = ScaleSpectrum(Spectrum,5,H)
    
    #tu jest potencjalnie jakis sporadical
    Bargraph = PrepareBargraph(np.around(Spectrum,0).astype(int),2)
   
    #for x in range(MAX7219_ROW):
    #    Max7219Write(SPI_CTX,REG_DIGIT0+x,int(Bargraph[x]))
       
 
    print("Iter: ",i)
    print("Spectrum: ",Spectrum)
    i += 1
    #break

 
    
  
print("Koniec czytania pliku .wav")

#End of script
matrix7219.Matrix7219Close()
print("Koniec skryptu")