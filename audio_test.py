# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 23:34:40 2016

@author: M
"""

"""PyAudio Example: Play a WAVE file."""

import pyaudio
import wave

CHUNK = 1024
FileName = "test4.wav"
wf = wave.open(FileName, 'rb')

p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

data = wf.readframes(CHUNK)

while data != '':
    stream.write(data)
    data = wf.readframes(CHUNK)

stream.stop_stream()
stream.close()

p.terminate()
