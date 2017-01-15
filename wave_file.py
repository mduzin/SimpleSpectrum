import wave
import struct
import math
import numpy as np
import matplotlib.pyplot as plt
 
 
def DivideList(Spectrum,N,aggr_func):
    
    #metoda na przyspieszenie, pod warunkiem ze szerokosci przedzialow beda takie same
    if 0==(len(Spectrum)%N):
        return aggr_func(np.reshape(Spectrum,(N,len(Spectrum)/N)))
    
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
 
#FileName = "WaveTest.wav"
#FileName = "test.wav"
FileName = "test6.wav"
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
FPS = 27
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
        Spectrum[n] = Spectrum[n][range(math.floor(WaveChannelLen/2))]
        Spectrum[n] = abs(Spectrum[n])
 
        #teraz dzielimy nasze spectrum na N przedzialow
        #N - ilosc przedzialow
        #BarRange - ilosc prazakow czestotliwosci przypadajacych na pojedynczy przedzial
        N=16
        BarSpectrum.append(DivideList(Spectrum[n],N,max))
        
 
    #rysuj/updatuj wykres widma
    plt.figure(1)
    plt.ylabel('Amplitude')
    plt.xlabel('Czestoliwosc [Hz]')
    plt.title('Widmo')
    plt.ylim(0.0, 32000.0)
    #plt.plot(abs(Spectrum[0]),'r')
    plt.bar(np.arange(N),BarSpectrum[0])
    plt.grid(True)
    plt.show()
 
    print("Iter: ",i)
    print("RealFrameNum: ",RealFrameNum )
    print("len(WaveChannel[0]): ",len(WaveChannel[0]))
    i += 1;
    FramesNum = WindowShift
 
    
  
print("Koniec czytania pliku .wav")