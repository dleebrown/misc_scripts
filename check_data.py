__author__ = 'donald'
#just basic open up a fits file, dig around to see what it's like
#
#
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import math
from scipy.interpolate import interp1d
filepath='/home/donald/Desktop/gregwork/new_g102/'
hdulist=fits.open(filepath+'IRC0218A_JOIN_26185.multifit.pz.fits')
hdulist.info()
scidata=np.array(hdulist[3].data)
scidata2=np.array(hdulist[4].data)
joined=np.zeros((len(scidata),2))
joined[:,0]=scidata
joined[:,1]=scidata2
print(joined)
