# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 23:39:16 2016

@author: M
"""

"""PyAudio Example: Play a wave file (callback version)"""

import pyaudio
import wave
import time

FileName = "test4.wav"
wf = wave.open(FileName, 'rb')

p = pyaudio.PyAudio()

def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    return (data, pyaudio.paContinue)

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)

stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

stream.stop_stream()
stream.close()
wf.close()

p.terminate()
