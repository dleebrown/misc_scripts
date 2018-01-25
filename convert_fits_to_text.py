"""writes a cl script that converts all fits files in a directory to text files using wspectext"""

import os

# set the directory containing the fits files
directory = '/home/donald/current_work/reduced_thesis_spectra_0118/continuum_fit'

filenames = os.listdir(directory)

fitsnames = []

for file in filenames:
    if '.fits' in file:
        # these are .cf.fits files most likely so remove the end
        fitsnames.append(file.strip('cf.fits'))

scriptname = open(directory+'/'+'textconvertscript.cl', mode='w')

# don't output the header

for line in fitsnames:
    scriptname.write('wspectext '+line+'.cf.fits '+line+'.txt header=no'+'\n')

scriptname.close()