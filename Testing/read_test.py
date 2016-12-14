import wave
import struct
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    data_size = 40000
    fname = "test.wav"
    frate = 11025.0
    wav_file = wave.open(fname, 'r')
    data = wav_file.readframes(data_size)
    wav_file.close()
    data = struct.unpack('{n}h'.format(n=data_size), data)
    data = np.array(data)

    w = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(w))
    print(freqs.min(), freqs.max())
    # (-0.5, 0.499975)

    # Find the peak in the coefficients
    idx = np.argmax(np.abs(w))
    freq = freqs[idx]
    freq_in_hertz = abs(freq * frate)
    print(freq_in_hertz)
    # 439.8975
    
    Ts = 1.0/Fs
    #Time axis
    t = np.arange(0,data_size/frate,1/frate)
    
    fig, ax = plt.subplots(2, 1)
    ax[0].plot(t,data)
    ax[0].set_xlabel('Time')
    ax[0].set_ylabel('Amplitude')
    ax[1].plot(freqs,abs(w),'r') # plotting the spectrum
    ax[1].set_xlabel('Freq (Hz)')
    ax[1].set_ylabel('|Y(freq)|')