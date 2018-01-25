"""script to generate a cl script to continuum-fit a bunch of fits files in a directory
assumes the iraf continuum routine is set to silent mode and has fit parameters dialed in
outputs a bunch of *.cl.fits files
"""

import os

# set the directory containing the fits files
directory = '/home/donald/current_work/reduced_thesis_spectra_0118'

filenames = os.listdir(directory)

fitsnames = []

for file in filenames:
    if '.fits' in file:
        # ignore any files already continuum-fit
        if not '.cf.fits' in file:
            fitsnames.append(file.strip('.fits'))

scriptname = open(directory+'/'+'continuumfitscript.cl', mode='w')

for line in fitsnames:
    scriptname.write('continuum '+line+' '+line+'.cf'+'\n')

scriptname.close()



