"""Generates a text file with dropin text to put into ANNA to run inference on a text file"""

import os

# set the directory containing the text files
directory = '/home/donald/current_work/reduced_thesis_spectra_0118/text_cf_spectra'

filenames = os.listdir(directory)

txtnames = []

for file in filenames:
    if '.txt' in file:
        txtnames.append(file)

outputfile = open(directory+'/'+'pasteme.txt', mode='w')

# don't output the header

for line in txtnames:
    outputfile.write('# if text mode used, text file with wavelength, flux columns\n')
    outputfile.write('TEXT_IMAGE: '+directory+'/'+str(line)+'\n\n')

outputfile.close()