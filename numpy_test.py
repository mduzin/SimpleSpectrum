# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 21:40:04 2017

@author: M
"""


import numpy as np

a = [1,-2,3,-4,5,-6,7,-8]

np_a = np.array(a).reshape((-1,2))

print(np_a)


np_b = np.arange(10)
print(np_b)

np_b = np.delete(np_b, np.s_[:2], None)

print(np_b)

np_b = np.delete(np_b, -1, None)

print(np_b)

np_a = np.delete(np_a, -1, 1)

print(np_a)

a = np.array([1,2,3,4,3,2,1,0])
b = np.array([1,2,3,4,3,2,1,0])
c = np.array([1,2,3,4,3,2,1,0])
d = np.array([1,2,3,4,3,2,1,0])


np_c = np.array([1,1,2,2,3,3,4,4,5,5,6,6]).reshape(-1,1)
print(np_c)

np_rfft =  np.absolute(np.fft.rfft(np_c,axis=0))
np_rfft =  np.delete(np_rfft, -1, 0)
np_rfft =  np.sum(np_rfft,axis=1)
print(np_rfft)