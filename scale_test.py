# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 21:00:53 2016

@author: M
"""

import math
import numpy as np

Array = np.array([50,90,1234,545,-50,-190,-1234,-54])

OldRange = {'max':100, 'min':-100}
NewRange = {'max': 10, 'min':-10}

a = (NewRange['min']-NewRange['max'])/(OldRange['min']-OldRange['max'])
b = NewRange['min'] - a*OldRange['min']

NewArray = a*Array +b

for i in range(len(NewArray)):
    if NewArray[i] > NewRange['max']:
        NewArray[i] = NewRange['max']
    if NewArray[i] < NewRange['min']:
        NewArray[i] = NewRange['min']