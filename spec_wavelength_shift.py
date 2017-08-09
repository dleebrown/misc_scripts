import numpy as np
import glob

wavelength_shift = 0.45

filelist = glob.glob('*.vsn.spec')
num_files = len(filelist)

test_file = np.genfromtxt(filelist[0])
num_px = np.size(test_file[:, 0])

for entry in range(num_files):
    curr_file = np.genfromtxt(filelist[entry])
    curr_file[:, 0] = curr_file[:, 0] + 0.45
    np.savetxt(filelist[entry], curr_file)
