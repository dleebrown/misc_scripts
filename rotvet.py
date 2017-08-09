# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 16:20:58 2014

@author: Donald
"""

# takes in a folder of robospect outputs, where the .robolines files have been turned into .robolines.txt files. calculates
#the rotational velocity for each output file using the calculated fwhm for the following lines: 6643ni, 6677fe, 6717ca, 6721si, 6750fe,
#6767ni, 6820fe. Subtracts an assumed instrumental broadening of 0.5A in quadrature from each calculated fwhm (see 6819 paper 
#for rationale behind particular value), rejecting any fwhm that would result in negative corrected fwhm. Calculates the rotvet
#for each corrected line using the approximation of fekel 1997 (for FGK dwarfs), and writes the mean and std. rotvets to output file. 
#rejects any star for which there are 3 or more rejected fwhms. 

import os
import numpy as np
import math

inputfolder=str(raw_input('Input folder with .robolines.txt, path is desktop: '))
outputfile = str(raw_input('Output file to contain rotvets, path is desktop: '))

deskpath = "C:\\Users\\Donald\\Desktop\\"
inputfolder = deskpath+inputfolder
outputfile = deskpath+outputfile+'.txt'

contents = os.listdir(inputfolder)
filename = []

for item in contents:
    if "robolines" in item:
        filename.append(item)
    else:
        cookies=1

iters=len(filename)

erotvets = []
allrotvets = []
for x in range(iters):
    templistfwhm = []
    currentfileloc = inputfolder+'\\'+filename[x]
    currentfile = open(currentfileloc,'r')
    #print("file opened")
    for line in currentfile:
        splitit = line.split()
        if "6643.63" in splitit and "1.68" in splitit:
            templistfwhm.append(splitit[2])
            #print('6643ni found')
        if "6677.99" in splitit and "2.56" in splitit:
            templistfwhm.append(splitit[2])
            #print('6677fe found')
        if "6717.68" in splitit and "2.71" in splitit:
            templistfwhm.append(splitit[2])
            #print('6717ca found')
        if "6721.85" in splitit and "5.86" in splitit:
            templistfwhm.append(splitit[2])
            #print("6721si found')
        if "6750.15" in splitit and "2.42" in splitit:
            templistfwhm.append(splitit[2])
            #print('6750fe found')
        if "6767.77" in splitit and "1.83" in splitit:
            templistfwhm.append(splitit[2])
            #print('6767ni found')
        if "6820.37" in splitit and "4.64" in splitit:
            templistfwhm.append(splitit[2])
            #print('6820fe found')
        else:
            cookies = 2


    templistfwhm2 = []
    for entry in templistfwhm:
        templistfwhm2.append(float(entry))
    tempstdfwhm = templistfwhm2 #temporary array to calculate std
    #meanfw = 2.355*(np.median(templistfwhm2)) #calculates mean fwhm from all fwhm
    
    #calculates std
    finalfwhm = []
    for entry in range(len(tempstdfwhm)):
        tempstdfwhm[entry] = tempstdfwhm[entry]*2.355
        if tempstdfwhm[entry]*tempstdfwhm[entry] > .25:   
            tempstdfwhm[entry] = math.sqrt(tempstdfwhm[entry]*tempstdfwhm[entry]-0.25) #removes an assumed instrumental broadening in fwhm of 0.5A (6819 paper gives 2.5px at 0.2A/px)
            finalfwhm.append(84.5154*(math.sqrt(tempstdfwhm[entry]+1.0833)-1.06025)) #calculation of rotvet using fekel 1997 (PASP)
        else:
            candycanes = 2
            #print("warning, fwhm rejected (too low)")

#may want to correct for macroturbulent velocity at a later date - minor correction now given the uncertainties in the data i think
        
    rotvet = np.mean(finalfwhm) #calculation of rotvet using fekel 1997 (PASP)
    erotvet = np.std(finalfwhm) #calculation of error in rotvet
    if len(finalfwhm) >= 4: #rejects any rotvet calcs where 3 or more lines have fwhm lower than 0.5A       
        allrotvets.append(rotvet)     
        erotvets.append(erotvet)
    else: 
        allrotvets.append("NA")
        erotvets.append("NA")
        print("star rejected (too many low fwhm)")
    currentfile.close()
    
output = open(outputfile,'w')
for x in range(iters):
    snakes=filename[x]
    snakes = snakes.split('robolines')
    snakes=snakes[0]
    snakes = snakes.split('_')
    snakes = snakes[0]
    output.write(str(snakes)+' '+str(allrotvets[x])+' '+str(erotvets[x])+' \n')

output.close()
        
        