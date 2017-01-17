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