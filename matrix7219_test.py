# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 14:17:28 2017

@author: M
"""

import matrix7219

MATRIX_CTX = matrix7219.Matrix7219Open(n=2)
matrix7219.Matrix7219Init(MATRIX_CTX)
matrix7219.Matrix7219Clean(MATRIX_CTX)
matrix7219.Matrix7219Close()