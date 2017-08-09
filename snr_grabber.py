# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 16:20:58 2014

@author: Donald
"""

# takes in a folder of robospect outputs, where the .robospect files have been turned into .robospect.txt files. calculates
#the SNR for each output file using the 6680-6694 measured flux and the estimated error for the star. outputs a table of 
#these calculated SNRs. 

import os

inputfolder=str(raw_input('Input folder with .robospect.txt, path is desktop: '))
outputfile = str(raw_input('Output file to contain SNRs, path is desktop: '))

deskpath = "C:\\Users\\Donald\\Desktop\\"
inputfolder = deskpath+inputfolder
outputfile = deskpath+outputfile+'.txt'

contents = os.listdir(inputfolder)
filename = []

for item in contents:
    if "robospect" in item:
        filename.append(item)
    else:
        cookies=1

iters=len(filename)

allsnrs = []
for x in range(iters):
    templistwave=[]
    templistflux=[]
    templisterr=[]
    templistsnr=[]
    currentfileloc = inputfolder+'\\'+filename[x]
    currentfile = open(currentfileloc,'r')
    for line in currentfile:
        splitit = line.split()
        templistwave.append(splitit[0])
        templistflux.append(splitit[1])
        templisterr.append(splitit[2])
    templistwave = templistwave[2:]
    templistflux = templistflux[2:]
    templisterr = templisterr[2:]
    length = len(templistwave)
    for item in range(len(templistwave)):
        if float(templistwave[item]) > 6686 and float(templistwave[item]) < 6691:
            templistsnr.append(float(templistflux[item])/float(templisterr[item]))
        else:
            cookies = 2
    allsnrs.append(sum(templistsnr)/len(templistsnr))
    currentfile.close()
    
output = open(outputfile,'w')
for x in range(iters):
    snakes=filename[x]
    snakes = snakes.split('robospect')
    snakes=snakes[0]
    output.write(str(snakes)+' '+str(allsnrs[x])+' \n')

output.close()

print(allsnrs)
print(sum(allsnrs)/len(allsnrs))
        
        