import numpy as np
import glob

filelist = glob.glob('*.spec.i')
num_stars = len(filelist)

grab_px = np.genfromtxt(filelist[0])
num_px = np.size(grab_px[:, 0])

allspec = np.zeros((num_px, num_stars+1))
allspec[:, 0] = grab_px[:, 0]
for entry in range(num_stars):
    spectrum = np.genfromtxt(filelist[entry])
    allspec[:, entry+1] = spectrum[:, 1]

median_spec = np.zeros((num_px, 2))

median_spec[:, 0] = grab_px[:, 0]
median_spec[:, 1] = np.median(allspec[:, 1:], axis=1)

np.savetxt('median_solar_spec', median_spec)
