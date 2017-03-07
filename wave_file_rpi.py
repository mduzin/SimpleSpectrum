#Topmost script file

import sys
import wave
import struct
import math
import numpy as np
import matrix7219
import pyaudio

#Send spectrum bargraph to Matrix MAX7219
def SendBargraphToMatrix(Bargraph,Matrix_Ctx):
    if Bargraph.size == Matrix_Ctx['N']:
        n = Matrix_Ctx['n']
        REG_ARR = Matrix_Ctx['REG_ARR']
        Bargraph = np.fliplr(Bargraph)
        Bargraph = np.insert(Bargraph,np.arange(n),REG_ARR,axis=1)
        matrix7219.Matrix7219SendMatrixData(Matrix_Ctx,Bargraph)
    return

#Convert Spectrum array into matrix max7219 bargraph array
def PrepareBargraph(Spectrum,Matrix_Ctx):
    if Spectrum.size == Matrix_Ctx['N']:
        #sprawdzamy czy wartosci mieszcza sie w zakresie, jak nie to obetnij do zakresu <0,H>
        Spectrum = np.clip(Spectrum,0,Matrix_Ctx['H'])
        #musimy podzielic Spectrum na n wyswietlaczy
        BAR_ARR = Matrix_Ctx['BAR_ARR']
        Spectrum = Spectrum.reshape(n,-1)
        Bargraph = []
        for max7219bars in Spectrum:
            Bars = np.vstack((BAR_ARR[item] for item in max7219bars))
            Bars = np.packbits(Bars, axis=0).flatten()
            Bargraph.append(Bars)
        return np.array(Bargraph).transpose()
    else:
        return np.array([0])

# Aggregate data from rfft operation 
# IN Spectrum - spectrum from numpy.rfft transformation
# IN N - number of spectrum bars
# OUT - Aggregated spectrum numpy array [array shape: (N,)]
def AggregateList(Spectrum,N):
    if Spectrum.size > N:
        #in order to accelerate aggregation we number of Spectrum frames must be dividable by N
        if 0!=(Spectrum.size%N):
            DivideLength = Spectrum.size - Spectrum.size%N
            #delete x last items from Spectrum in order to meet "dividable by N" requirement
            Spectrum = np.delete(Spectrum,np.s_[DivideLength:],0)

            Spectrum = np.reshape(Spectrum,(N,Spectrum.size//N))
            return np.average(Spectrum, axis=1)
    else:
        return np.array([0])


#Scale aggregated Spectrum
# IN Spectrum - aggregated spectrum data
# IN OldMax - old maximum allowed value in Spectrum
# IN NewMax - new maximum allowed value in Spectrum
# OUT - Scaled Spectrum
def ScaleSpectrum(Spectrum,OldMax,NewMax):
    #Saturation filter
    if 0 != OldMax:
        ScaleSpectrum = np.clip(Spectrum,0,OldMax)
        return np.around((ScaleSpectrum*NewMax)/OldMax)
    else:
        return np.array([0])
 
# Send rfft spectrum to matrix max7219 display
# IN Spectrum - spectrum from numpy.rfft transformation
# IN Matrix_Ctx - Matrix MAX7219 object handle
def SendSpectrumToMatrix(Spectrum,Matrix_Ctx):
    Spectrum = AggregateList(Spectrum,Matrix_Ctx['N'])
    Spectrum = ScaleSpectrum(Spectrum,32,Matrix_Ctx['H'])
    Bargraph = PrepareBargraph(np.around(Spectrum,0).astype(int),Matrix_Ctx)
    SendBargraphToMatrix(Bargraph,Matrix_Ctx)
    return

#----Script Start----
if __name__ == "__main__":

    #Global variables and settings
    #FileName - .wav file to proceed
    #<TODO:> Check filename argument
    #FPS - Frames per second to display
    #n - Number of max7219 displays serially connected
    FileName = sys.argv[1]
    FPS = 27   #FPS
    n = 2

    MATRIX_CTX = matrix7219.Matrix7219Open(n=2)
    matrix7219.Matrix7219Init(MATRIX_CTX)
    matrix7219.Matrix7219Clean(MATRIX_CTX)

    WaveObj = wave.open(FileName, mode='rb')
    print("Channels: ".ljust(25),WaveObj.getnchannels())
    print("Sample width: ".ljust(25),WaveObj.getsampwidth()," bytes")
    print("Sampling frequency: ".ljust(25),WaveObj.getframerate()," Hz")
    print("Number of audio frames: ".ljust(25),WaveObj.getnframes())
    print("Compression type: ".ljust(25),WaveObj.getcomptype(),"\n")

    WaveParams = WaveObj.getparams();

    #8-bit samples are stored as unsigned bytes, ranging from 0 to 255. 
    #16-bit samples are stored as 2's-complement signed integers, ranging from -32768 to 32767.
    #.wav file is always Little Endian so we use '<'
    FormatDict = {1:'B',2:'h',4:'i',8:'q'}

    #FramesLength - number of frames we need to calculate current spectrum, eqaul to sampling frequency
    #FramesShift  - number of frames over which we will shift our signal in single iteration (half of WindowLength)
    #WaveData     - array of frames from .wav file

    FramesLength = WaveParams.framerate
    FramesShift  = math.floor(WaveParams.framerate/FPS)
    WaveData     = np.zeros(FramesLength)

    #Open audio stream
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(WaveObj.getsampwidth()),
                    channels=WaveObj.getnchannels(),
                    rate=WaveObj.getframerate(),
                    output=True)

    i=0
    while True:
        #read new frames from .wav file
        WaveFrame = WaveObj.readframes(FramesShift)

        #end of frames - loop exit
        if not WaveFrame: break

        #play audio frames
        stream.write(WaveFrame)

        #Program flow:
        #1. create numpy array for audio frames (initialize with zeros) (done outside loop)
        #2. read new data from filew with WaveObj.readframes()
        #3. delete the oldest frame from WaveFrame using numpy.delete()
        #4. add new frames using numpy.append()
        #5. Split WaveData into channels using numpy.reshape()
        #6. perfrom numpy.rfft() only for first channel
        RealFramesLength = len(WaveFrame)//(WaveParams.sampwidth*WaveParams.nchannels)
        WaveFrame = struct.unpack('<{n}{t}'.format(n=RealFramesLength*WaveParams.nchannels,t=FormatDict[WaveParams.sampwidth]),WaveFrame)
        WaveData = np.delete(WaveData, np.s_[0:len(WaveFrame)], None)
        WaveData = np.append(WaveData,WaveFrame)
        WaveChannel = np.array(WaveData).reshape(-1,WaveParams.nchannels)

        #rfft for all channels:
        #Spectrum = np.absolute(np.fft.rfft(WaveChannel,axis=0))
        # sum all channels
        #Spectrum = np.sum(Spectrum,axis=1)

        #rfft only for first channel:
        WaveChannel = WaveChannel[:,0]
        if 0 != WaveChannel.sum():
            Spectrum = np.absolute(np.fft.rfft(WaveChannel))
            #convert to dB scale and use power of ^2 (for better visualization purpose)
            np.place(Spectrum, Spectrum < 1, 1)
            Spectrum = np.log10(Spectrum)**2
        else:
            Spectrum = np.array([0])

        SendSpectrumToMatrix(Spectrum,MATRIX_CTX)

        print("Iter: ",i)
        #print("Spectrum: ",Spectrum)
        i += 1
        #break

    print("End of .wav file")
    stream.stop_stream()
    stream.close()
    p.terminate()
    matrix7219.Matrix7219Clean(MATRIX_CTX)
    matrix7219.Matrix7219Close()
    print("End od script. Bye")
#----End of script----
