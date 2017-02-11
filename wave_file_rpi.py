import wave
import struct
import math
import numpy as np
import matrix7219
import pyaudio
 
 
#Zmienne globalne i Nastawy


#Plik do analizy
#<TODO:> plik wczytywany jako parametr wejsciowy
FileName = "test6.wav"
#FileName = "vega.wav"

#Ilosc klatek na sek do wyswietlenia
FPS = 23   #FPS-ilosc klatek na sekunde 

#Ilosc wyswietlaczy max7219
n = 2


#zmienna pomocnicza
LastBargraph = np.zeros((8,n*2), dtype=int)

def SendBargraphToMatrix(Bargraph,Matrix_Ctx):
    n = Matrix_Ctx['n']
    REG_ARR = Matrix_Ctx['REG_ARR']
    Bargraph = np.fliplr(Bargraph)
    Idx = np.arange(n)
    Bargraph = np.insert(Bargraph,Idx,REG_ARR,axis=1)
    global LastBargraph
    DiffBargraph = LastBargraph - Bargraph
        
    for diff_row,row in zip(DiffBargraph,Bargraph):
        if 0 != sum(diff_row):
            int_row = [int(x) for x in row]
            matrix7219.Matrix7219Write(int_row)
    LastBargraph = Bargraph
    return

#<TODO:> komentarz
def PrepareBargraph(Spectrum,Matrix_Ctx):
    #wpierw musimy podzielic Spectrum na n wyswietlaczy
    BAR_ARR = Matrix_Ctx['BAR_ARR']
    Spectrum = Spectrum.reshape(n,-1) 
    Result = []
    for max7219bars in Spectrum:
        Bars = np.vstack((BAR_ARR[item] for item in max7219bars))
        Bars = np.packbits(Bars, axis=0).flatten()
        Result.append(Bars)
    return np.array(Result).transpose()
    return

#<TODO:> komentarz    
#<TODO:>obciac x ostatnich probek z Spectrum tak zeby bylo podzielne przez N i korzystac tylko z numpy
def DivideList(Spectrum,N):
    #metoda na przyspieszenie, pod warunkiem ze szerokosci przedzialow beda takie same
    if 0!=(Spectrum.size%N):
        DivideLength = Spectrum.size - Spectrum.size%N
        Spectrum = np.delete(Spectrum,np.s_[DivideLength:],0)
   
    Spectrum = np.reshape(Spectrum,(N,Spectrum.size//N))
    return np.average(Spectrum, axis=1)  
  
        
#<TODO:> komentarz    
def ScaleSpectrum(Spectrum,OldMax,NewMax):
    #Saturation filter
    SatSpectrum = np.clip(Spectrum,0,OldMax)
    #Scale array
    ScaleSpectrum = np.array(SatSpectrum)
    return np.around((ScaleSpectrum*NewMax)/OldMax)
 

def SendSpectrumToMatrix(Spectrum,Matrix_Ctx): 
       
    Spectrum = DivideList(Spectrum,Matrix_Ctx['N'])
    #<TODO:> Obmyslec lepszy sposob skalowania max'a
    Spectrum = ScaleSpectrum(Spectrum,32,Matrix_Ctx['H'])
    
    #tu jest potencjalnie jakis sporadical
    Bargraph = PrepareBargraph(np.around(Spectrum,0).astype(int),Matrix_Ctx)
    SendBargraphToMatrix(Bargraph,Matrix_Ctx)    
    return

#----Script Start----
    
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
FramesLength = WaveParams.framerate
FramesShift  = math.floor(WaveParams.framerate/FPS)
WaveData     = np.zeros(FramesLength)

p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(WaveObj.getsampwidth()),
                channels=WaveObj.getnchannels(),
                rate=WaveObj.getframerate(),
                output=True)   
 
print("ilosc ramek1: ",WaveObj.getnframes())
#wczytamy wszystkie ramki na raz
WaveFrames = WaveObj.readframes(WaveObj.getnframes())
print("ilosc ramek2: ",len(WaveFrames))

startIndex = 0
multiply = WaveObj.getnchannels()*WaveObj.getsampwidth()
stopIndex = FramesShift * multiply

i=0
while True:
    #pobieramy nowe ramki z pliku
    #WaveFrame = WaveObj.readframes(FramesShift)
    WaveFrame = WaveFrames[startIndex:stopIndex]
    startIndex = stopIndex
    stopIndex = stopIndex + (FramesShift * multiply)
    
    #jesli nie ma wiecej ramek to wyjdz z petli
    if not WaveFrame: break

    stream.write(WaveFrame)
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
    #Spectrum = np.absolute(np.fft.rfft(WaveChannel,axis=0))
    # oraz sumujemy wszystkie kanaly
    #Spectrum = np.sum(Spectrum,axis=1)
    
    #<TODO:>liczymy tylko kanal 1
    Spectrum = np.absolute(np.fft.rfft(WaveChannel[:,0]))
    
    #przejscie na decybele,podnoszenie ^2 tylko dla celow wizualizacyjnych
    Spectrum = np.log10(Spectrum)**2
    
    SendSpectrumToMatrix(Spectrum,MATRIX_CTX)
 
    
    print("Iter: ",i)
    #print("Spectrum: ",Spectrum)
    i += 1
    #break

     
  
print("Koniec czytania pliku .wav")
stream.stop_stream()
stream.close()
p.terminate()
matrix7219.Matrix7219Clean(MATRIX_CTX)
matrix7219.Matrix7219Close()
print("Koniec skryptu")
#----End of script----
