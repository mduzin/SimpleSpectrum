import wave
import os
import sys
 
FileName = "test.wav"
 
WaveObj = wave.open(FileName, mode='rb')
 
print("Channels: ".ljust(25),WaveObj.getnchannels())
print("Sample width: ".ljust(25),WaveObj.getsampwidth()," bytes")
print("Sampling frequency: ".ljust(25),WaveObj.getframerate()," Hz")
print("Number of audio frames: ".ljust(25),WaveObj.getnframes())
print("Compression type: ".ljust(25),WaveObj.getcomptype(),"\n")
 
WaveParams = WaveObj.getparams(); print("Params: ".ljust(25),WaveParams, "\n")
 
#chcialbym zeby chunk mial 100 probek/frame'ow/ramek, niezaleznie ile jest kanalow 
ChunkSize = 100
while True:
    WaveFrame = WaveObj.readframes(1)
    if not WaveFrame: break
    #Przetwarzanie ramki 
 
    #wydrukuj poszegolne ramki
    #print("Raw: ",WaveFrame, end=" ")
 
    for Channel in range(WaveParams.nchannels):
       StartIndex = Channel * WaveParams.sampwidth
       StopIndex  = StartIndex + WaveParams.sampwidth
       print("Channel ", Channel,": ",WaveFrame[StartIndex:StopIndex], end=" ") 
       BytesSample = WaveFrame[StartIndex:StopIndex]
    print("")
 
 
 
print("Koniec pliku .wav")
 
 
WaveObj.close()
