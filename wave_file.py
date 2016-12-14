import wave
import struct
import numpy as np
import math
import matplotlib.pyplot as plt

 
FileName = "test5.wav"
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
    #zapisz ramke jako tuplet
    WaveData.append(struct.unpack(WaveFmt, WaveFrame))
   
print("Koniec czytania pliku .wav")
WaveObj.close()

#We are done with .wav file. All information we need are in
#WaveParams and WaveData variables    

#number of frames we need to calculate current spectrum, eqaul to sampling frequency
WindowLength = WaveParams.framerate
#num of frames over which we will shift our signal
WindowShift  = math.floor(WaveParams.framerate/2)



#<TODO:> zrobic jako pojedynca petla
WaveChannel = []
for n in range(WaveParams.nchannels):
    WaveChannel.append([sample[n] for sample in WaveData])



#Acquire window of samples
StartIndex = 0 # pozniej bedzie obliczane to w petli o kroku (StartIndex += WindowShift)

#nie wiem czy nie musze zrobic zero-padding jesli mam mnie probek niz dlugosc zasaniczej ramki
WaveWindow = np.array(WaveData[StartIndex:(StartIndex+WindowLength)])
RealWindowLength = len(WaveWindow)

#if RealWindowLength < WindowLength: 
#    WaveWindow = WaveWindow + [0]*(WindowLength - RealWindowLength) # zamiast [0], musi byc wlasciwa struktura

#narazie spectrum tylko dla kanalu 0
Spectrum = []
for n in range(WaveParams.nchannels):
    Spectrum.append((2/RealWindowLength)*np.fft.fft(WaveChannel[n]))
    Spectrum[n] = Spectrum[n][range(math.floor(RealWindowLength/2))]
    
#prepare additional data for plot    
#Sampling rate
Fs = WaveParams.framerate
#Sampling interval
Ts = 1.0/Fs
#Time axis
t = np.arange(StartIndex*Ts,(StartIndex+RealWindowLength)*Ts,Ts)
#Time lenght of analyzed frame [s]
T = RealWindowLength/Fs
#Frequency axis
frq = np.arange(RealWindowLength)/T
#reduce to Nyquist frequency
frq = frq[range(math.floor(RealWindowLength/2))] 


#fig, ax = plt.subplots(2, 1)
#ax[0].plot(t,WaveWindow)
#ax[0].set_xlabel('Time')
#ax[0].set_ylabel('Amplitude')
#ax[1].plot(frq,abs(Spectrum),'r') # plotting the spectrum
#ax[1].set_xlabel('Freq (Hz)')
#ax[1].set_ylabel('|Y(freq)|')
