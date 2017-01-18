# your code goes here
import math
import wave
import struct
import numpy as np
 
#nagrywane czestotliwosci
freq_list = [440.0,2200.0, 4400.0]
 
#ilosc ramp
ramp_count = 10
 
#ile czasu ma trwac nagranie[s]
rec_length = 30
 
#nazwa pliku
fname = "test6.wav"
 
#czestoliwosc probkowania
frate = 11025.0  # framerate as a float
 
#Amplituda +/- 32000
amp = 64000.0/len(freq_list)     # multiplier for amplitude
 
#ilosc frame'ow
data_size = math.floor(rec_length * frate)
print("data_size:", data_size)
#ilosc framow podzielna przez 2*ilosc ramp
data_size_ramp = data_size//(2*ramp_count) 
data_size = data_size_ramp * (2*ramp_count)
 
print("data_size:", data_size)
 
t = np.linspace(0,rec_length,data_size)
print(t)
sine_list_x = sum([np.sin(2*np.pi*f*t) for f in freq_list])
ramp_up = np.linspace(0., 1., data_size_ramp)
ramp_down = np.linspace(1., 0., data_size_ramp)
ramp = np.concatenate((ramp_up,ramp_down)*ramp_count)
 
sine = sine_list_x * ramp
 
wav_file = wave.open(fname, "w")
 
nchannels = 1
sampwidth = 2
framerate = int(frate)
nframes = int(data_size)
comptype = "NONE"
compname = "not compressed"
 
wav_file.setparams((nchannels, sampwidth, framerate, nframes,
    comptype, compname))
 
for s in sine:
    # write the audio frames to file
    wav_file.writeframes(struct.pack('h', int(s*amp/2)))
 
wav_file.close()