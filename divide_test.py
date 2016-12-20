# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 21:46:31 2016

@author: M
"""

import numpy as np

a = [1,2,3,4,5,6,7,8]*9

arr = np.array(a)
N = 8
    
#metoda na przyspieszenie, pod warunkiem ze szerokosci przedzialow beda takie same
arr = np.reshape(arr,(N,arr.size/N))
max_arr = np.amax(arr, axis=1)   
 