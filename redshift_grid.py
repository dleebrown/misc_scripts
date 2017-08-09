__author__ = 'donald'
#see how fine the redshift grid is
from astropy.io import fits
import numpy as np

image1=fits.open('/home/donald/Desktop/gregwork/PYTHON/redshift_range/IRC0218A_JOIN_26185.multifit.pz.fits')
#image1.info()
cont1d=image1[1].data
cont1d=np.array(cont1d)
line1d=image1[3].data
line1d=np.array(line1d)
test=[]
for entry in range(len(line1d)-1):
    test.append(line1d[entry]-line1d[entry+1])
print np.mean(test)
print(np.max(test))

image2=fits.open('/home/donald/Desktop/gregwork/PYTHON/redshift_range/IRC0218A_JOIN_26383.multifit.pz.fits')
#image2.info()
cont1d=image2[1].data
cont1d=np.array(cont1d)
line1d=image2[3].data
line1d=np.array(line1d)
test=[]
for entry in range(len(line1d)-1):
    test.append(line1d[entry]-line1d[entry+1])
print np.mean(test)
print np.max(test)

image3=fits.open('/home/donald/Desktop/gregwork/PYTHON/redshift_range/IRC0218A_JOIN_26389.multifit.pz.fits')
#image3.info()
cont1d=image3[1].data
cont1d=np.array(cont1d)
line1d=image3[3].data
line1d=np.array(line1d)
test=[]
for entry in range(len(line1d)-1):
    test.append(line1d[entry]-line1d[entry+1])
print np.mean(test)
print np.max(test)

image4=fits.open('/home/donald/Desktop/gregwork/PYTHON/redshift_range/IRC0218A_JOIN_26496.multifit.pz.fits')
#image4.info()
cont1d=image4[1].data
cont1d=np.array(cont1d)
line1d=image4[3].data
line1d=np.array(line1d)
test=[]
for entry in range(len(line1d)-1):
    test.append(line1d[entry]-line1d[entry+1])
print np.mean(test)
print np.max(test)

image1=fits.open('/home/donald/Desktop/gregwork/PYTHON/redshift_range/IRC0218A_JOIN_26514.multifit.pz.fits')
#image1.info()
cont1d=image1[1].data
cont1d=np.array(cont1d)
line1d=image1[3].data
line1d=np.array(line1d)
test=[]
for entry in range(len(line1d)-1):
    test.append(line1d[entry]-line1d[entry+1])
print np.mean(test)
print(np.max(test))

image2=fits.open('/home/donald/Desktop/gregwork/PYTHON/redshift_range/IRC0218A_JOIN_26542.multifit.pz.fits')
#image2.info()
cont1d=image2[1].data
cont1d=np.array(cont1d)
line1d=image2[3].data
line1d=np.array(line1d)
test=[]
for entry in range(len(line1d)-1):
    test.append(line1d[entry]-line1d[entry+1])
print np.mean(test)
print np.max(test)

image3=fits.open('/home/donald/Desktop/gregwork/PYTHON/redshift_range/IRC0218A_JOIN_26559.multifit.pz.fits')
#image3.info()
cont1d=image3[1].data
cont1d=np.array(cont1d)
line1d=image3[3].data
line1d=np.array(line1d)
test=[]
for entry in range(len(line1d)-1):
    test.append(line1d[entry]-line1d[entry+1])
print np.mean(test)
print np.max(test)

image4=fits.open('/home/donald/Desktop/gregwork/PYTHON/redshift_range/IRC0218A_JOIN_27054.multifit.pz.fits')
#image4.info()
cont1d=image4[1].data
cont1d=np.array(cont1d)
line1d=image4[3].data
line1d=np.array(line1d)
test=[]
for entry in range(len(line1d)-1):
    test.append(line1d[entry]-line1d[entry+1])
print np.mean(test)
print np.max(test)