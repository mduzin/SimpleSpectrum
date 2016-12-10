import wave
import struct
import numpy as np
import math
import matplotlib.pyplot as plt

def ByteListToNum(bytes):
  return int(bytes.encode('hex'), 16)
 
FileName = "test4.wav"
WaveObj = wave.open(FileName, mode='rb')
 
print("Channels: ".ljust(25),WaveObj.getnchannels())
print("Sample width: ".ljust(25),WaveObj.getsampwidth()," bytes")
print("Sampling frequency: ".ljust(25),WaveObj.getframerate()," Hz")
print("Number of audio frames: ".ljust(25),WaveObj.getnframes())
print("Compression type: ".ljust(25),WaveObj.getcomptype(),"\n")
 
WaveParams = WaveObj.getparams(); #print("Params: ".ljust(25),WaveParams, "\n")


#8-bit samples are stored as unsigned bytes, ranging from 0 to 255. 
#16-bit samples are stored as 2's-complement signed integers, ranging from -32768 to 32767.
FormatDict = {1:'B',2:'h',4:'i',8:'q'}

#.wav file is always Little Endian so we use '<'
WaveFmt = '<' + FormatDict[WaveParams.sampwidth]*WaveParams.nchannels
print(WaveFmt)

WaveData = []
while True:
    WaveFrame = WaveObj.readframes(1)
    if not WaveFrame: break
    #Przetwarzanie ramki 
 
    #zapisz ramki
    WaveData.append(struct.unpack(WaveFmt, WaveFrame))
   
print("Koniec czytania pliku .wav")
WaveObj.close()

#We are done with .wav file. All information we need are in
#WaveParams and WaveData variables    

#number of frames we need to calculate current spectrum, eqaul to sampling frequency
WindowLength = 20#WaveParams.framerate
#num of frames over which we will shift our signal
WindowShift  = math.floor(WaveParams.framerate/2)



WaveChannel = []
for n in range(WaveParams.nchannels):
    WaveChannel.append([sample[0] for sample in WaveData])



#Acquire window of samples
StartIndex = 0 # pozniej bedzie obliczane to w petli o kroku (StartIndex += WindowShift)

#nie wiem czy nie musze zrobic zero-padding jesli mam mnie probek niz dlugosc zasaniczej ramki
WaveWindow = WaveData[StartIndex:(StartIndex+WindowLength-5)]
RealWindowLength = len(WaveWindow)

#if RealWindowLength < WindowLength: 
#    WaveWindow = WaveWindow + [0]*(WindowLength - RealWindowLength) # zamiast [0], musi byc wlasciwa struktura

Spectrum = (2/RealWindowLength)*np.fft.fft(WaveWindow)
    
    
#teraz policzy widmo z pierwszej paczki
#SamplesNum = WaveParams.framerate 
#SpectrumWindow = WaveChannel0[0:SamplesNum]
#n = len(SpectrumWindow)

#Spectrum = (2/n)*np.fft.fft(SpectrumWindow)
#Spectrum = Spectrum[range(math.floor(n/2))]

#fs = SamplesNum
#Ts = 1/fs                     
#t = np.arange(0,1,Ts)

#frq = np.arange(math.floor(n/2)) # one side frequency range

#fig, ax = plt.subplots(2, 1)
#ax[0].plot(t,SpectrumWindow)
#ax[0].set_xlabel('Time')
#ax[0].set_ylabel('Amplitude')
#ax[1].plot(frq,abs(Spectrum),'r') # plotting the spectrum
#ax[1].set_xlabel('Freq (Hz)')
#ax[1].set_ylabel('|Y(freq)|')
