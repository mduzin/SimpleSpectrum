import wave
import os
import sys
import struct

def ByteListToNum(bytes):
  return int(bytes.encode('hex'), 16)
 
FileName = "test1.wav"
WaveObj = wave.open(FileName, mode='rb')
 
print("Channels: ".ljust(25),WaveObj.getnchannels())
print("Sample width: ".ljust(25),WaveObj.getsampwidth()," bytes")
print("Sampling frequency: ".ljust(25),WaveObj.getframerate()," Hz")
print("Number of audio frames: ".ljust(25),WaveObj.getnframes())
print("Compression type: ".ljust(25),WaveObj.getcomptype(),"\n")
 
WaveParams = WaveObj.getparams(); print("Params: ".ljust(25),WaveParams, "\n")

FormatDict = {1:'B',2:'H',4:'I',8:'Q'}

WaveFmt = '<' + FormatDict[WaveParams.sampwidth]*WaveParams.nchannels
print(WaveFmt)

print(struct.unpack(WaveFmt, WaveObj.readframes(1)))

while True:
    WaveFrame = WaveObj.readframes(1)
    if not WaveFrame: break
    #Przetwarzanie ramki 
 
    #wydrukuj poszegolne ramki
    print(struct.unpack(WaveFmt, WaveFrame))
 
 
print("Koniec pliku .wav")
 
 
WaveObj.close()
