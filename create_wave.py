import math
import wave
import struct
import numpy as np
 
#nagrywane czestotliwosci
freq_list = [440.0, 4400.0]
 
#ile czasu ma trwac nagranie[s]
rec_length = 5
 
#nazwa pliku
fname = "test5.wav"
 
#czestoliwosc probkowania
frate = 11025.0  # framerate as a float
 
#Amplituda +/- 32000
amp = 64000.0/len(freq_list)     # multiplier for amplitude
 
#ilosc frame'ow
data_size = math.floor(rec_length * frate)
 
t = np.arange(0,rec_length,1/frate)
sine_list_x = sum([np.sin(2*np.pi*f*t) for f in freq_list])
x = np.linspace(0., 1., len(sine_list_x))

sine = sine_list_x * x
 
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