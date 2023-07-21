# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 19:00:05 2023

@author: sfs135
"""

import matplotlib.pyplot as plt
import numpy as np
import time
import io
from pyFDTD import pyFDTD

# %%

import sys
if len(sys.argv) > 1:
    NDim = int(sys.argv[1])
else:
    NDim = 2

# %% Run pyFDTD

start_time = time.time()

fdtd = pyFDTD(NDim=NDim, debug=True)

fdtd.t = 10e-3
# fdtd.setInputs()

# fdtd.gifFile = io.BytesIO()

fdtd.plotIthUpdate = 5
fdtd.doPlot = True
fdtd.saveRecData = False
fdtd.saveGif = False
# fdtd.showColBar = False

if fdtd.NDim == 1:
    # 1D Mesh
    fdtd.betaMode = 'varying'
    fdtd.mesh[0:10] = 1
    fdtd.mesh[90:] = 0.5
elif fdtd.NDim == 2:
    # # 2D mesh
    # fdtd.newEmptyMesh([200, 300])
    # fdtd.moveSrc([1.0, 0.75])
    # fdtd.srcFreq[0] = 1216
    # Load a 2D image
    fdtd.betaMode = 'varying'
    # fdtd.loadImage('../images/Flat_wall.png')
    fdtd.loadImage('../images/Binary_amplitude_diffuser.png')
    fdtd.moveSrc([1.0, 0.75])
elif fdtd.NDim == 3:
    # 3D mesh
    # fdtd.newEmptyMesh([80, 100, 50])
    ()

# Run
fdtd.run()

# with open("testFile.gif", "wb") as f:
#     f.write(fdtd.gifFile.getbuffer())

print("--- %s seconds ---" % (time.time() - start_time))

# %%

input('FINISHED!!\nPress key to exit.')

# %%

plt.close(fdtd.hf)

# %%

del(fdtd)

# %%

hf, ax = plt.subplots()

# p = np.array([[1,2],[3,4]])
# D = [1,1]

# hPlot = ax.imshow(p, \
#             extent=[0.0, D[1], 0.0, D[0]], \
#             aspect='equal', \
#             origin='lower')

# ax.set_xlim([0.25, 1])

xx = np.array([1])
yy = np.array([3])
onSlice = np.array([True])
col1 = (0.2,0.2,0.2,1)
col2 = (0.8,0.8,0.8,1)
cols = [col1]*len(xx)
for i in range(len(xx)):
    if not onSlice[i]:
        cols[i] = col2

hScat = ax.scatter(xx, yy, c=cols, marker="o")

# %%


# import numpy as np
# from PIL import Image, ImageSequence

# file1 = 'gifOut.gif'

# img = Image.open(file1)
# frames = np.array([np.array(frame.copy().convert('RGB').getdata(), dtype=np.uint8). \
#                    reshape(frame.size[1],frame.size[0],3) \
#                        for frame in ImageSequence.Iterator(img)])
    
    
# %%


# from scipy.io import wavfile
# import numpy as np
# import io

# # file = "example.wav"
# file = io.BytesIO()

# fs = 44100
# f = 100
# t = np.linspace(0., 1., fs)
# # A = np.iinfo(np.int16).max
# A = 1.0
# data = A*np.sin(2.0*np.pi*f*t)
# wavfile.write(file, fs, data)

# file.seek(0)
# print(file.read())
