"""given a folder of anna inferred outputs from the same trained model, concatenates the outputs into one file"""

import os
import numpy as np

# set the directory containing the text files
directory = '/home/donald/current_work/MY_THESIS/cleaned_r1'

filenames = os.listdir(directory)

txtnames = []

for file in filenames:
    if '.txt_infer.out' in file:
        txtnames.append(file)


# read first txt file
firsttxt = np.loadtxt(directory + '/' + txtnames[0], delimiter=',', skiprows=1, dtype='str')
firsttxt = np.reshape(firsttxt, (1, np.size(firsttxt)))

for line in txtnames[1:]:
    readtxt = np.loadtxt(directory+'/'+line, delimiter=',', skiprows=1, dtype='str')
    readtxt = np.reshape(readtxt, (1, np.size(readtxt)))
    firsttxt = np.concatenate((firsttxt, readtxt), axis=0)

np.savetxt(directory+'/'+'concatenated_outputs', firsttxt, fmt='%s')


#outputfile.close()