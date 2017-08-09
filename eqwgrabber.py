# -*- coding: utf-8 -*-
#
#EQWGRABBER
#Author: Donald Lee-Brown
#Updated: 05/27/2014
#
# Grabs eqws from a folder of robospect outputs
# need a folder (default folder location is desktop) filled with robospect outputs
# also need the linelist used ON THE DESKTOP (need to get in tab delimited csv) with ONLY LINES I CARE ABOUT
#linelist format is colums with titles: WL, excite, elm, ion
# program will go through all files, creating a text file with wavelength, species on left, eqws 
# listed columnwise with column title the filename of the measurements

#will need to change txt files extension in linux to .txt since they have .robolines assoc. with
#them in windows
#can do easily in elevated command prompt: navigate to the folder the lines are in in cmd,
#then type: ren *.robolines *.robolines.txt this will keep the robolines tag in the file too

#output is dumped to desktop as a text file

import os
inputfolder=str(raw_input('Input folder, path is desktop: '))
inputlist = str(raw_input('Linelist used, path is desktop: '))
outputfile = str(raw_input('output name, path is desktop: '))
deskpath = "C:\\Users\\Donald\\Desktop\\"
inputfolder = deskpath+inputfolder
inputlist = deskpath+inputlist+'.csv'
outputfile = deskpath+outputfile+'.txt'

contents = os.listdir(inputfolder)
filepathlist = []
filelistlong = []
for item in contents:
    if ".robolines" in item:
        filelistlong.append(item)
        filepathlist.append(inputfolder+'\\'+item)

filelist2 = []
for line in filelistlong:
    newstring = line.replace('.robolines', '')
    filelist2.append(newstring)

filelist =[]
for entry in filelist2:
    newstring = entry.split('_')
    filelist.append(newstring[0])
    

wavelist = []
elmlist = []
robolist = open(inputlist, 'r')
for line in robolist:
    snakes=line.split()
    wavelist.append(snakes[0])
    elmlist.append(snakes[2])

wavelist = wavelist[1:]
elmlist = elmlist[1:]

rowcount = len(elmlist)+1
colcount = len(filelist)

header = []
header2 = []
for number in range(colcount):
    header.append(filelist[number])
    header2.append(filelist[number])
header = ' '.join(header)
header = header + '\n'
workalot = open(outputfile, 'w')
workalot.write(header)
workalot.close()

snackalot = open(outputfile, 'a')
for burgers in range(len(wavelist)):
    temp = []
    for snakes in range(colcount):
        currentiter = open(filepathlist[snakes],'r')
        linepresent=False
        for line in currentiter:
            if wavelist[burgers] in line and elmlist[burgers] in line:
                linepresent=True
                wantthis = line.split()
                eqw = float(wantthis[12])

#for use if want to not have negative eqws show up in sorted output
#only for looking at consistency of a line's measurements, this output won't work
#with rest of scripts
#                if eqw < 0:
#                    temp.append('')
#                else:
#                    temp.append(wantthis[12])

#comment this out if using above expression
                temp.append(wantthis[12])
                #
        if not linepresent:
            print("warning, line "+wavelist[burgers]+" not found in star "+header2[snakes])
    temp = ' '.join(temp)
    temp = temp+'\n'
    snackalot.write(temp)

snackalot.close()


        




