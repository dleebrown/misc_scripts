# -*- coding: utf-8 -*-
#author: Donald Lee-Brown
#version: 3/9/2015
#ew_fe_compare: takes in a folder of moog input ew files, and the "all out" moogsifter output (in .csv form)
#and returns a file that gives a star-by-star, line-by-line comparison of ews and the resultant abundances
#useful for seeing if it's the ew measurements or the atmospheric models that are causing unwanted
#trends in calculated stellar abundances. 
#
#input: need a folder containing moog ew files named using the standard moog input format: X.xxx.txt
#also need a .csv sheet without delimiters merged (tab-delimited) that has the star-by-star,
#line-by-line abundance results from moog, with the titles as X.xxx(rot/bin)
#
#output: outputs 2 .txt files, each with columns for star, wavelength, element, ew, and a(x)
#one file will just have iron lines, one file will have all lines
#outputs with empty strings where no abundances were calculated (no ews), so when importing, don't
#merge delimiters. 
#other notes:
#folder of input moog files can ONLY contain the input .txt files (no other .txt files) 
#named as X.xxx (standard moogcreator output using normal conventions), since script just 
#grabs all .txt files in the target folder
#also will need to take moogsifter all line output and save as tab-delimed csv, also need to make sure
#wavelengths between two input file sets EXACTLY MATCH (including leading or trailing 0s - calc likes to truncate those)

import os

#I/O control
inputewfolder=str(raw_input('Input folder containing .txt moog ew inputs: '))
inputmoog=str(raw_input('moogsifter all abunds output .csv: '))
feoutput = str(raw_input('fe output name, path is desktop: '))
alloutput = str(raw_input('all elm output name, path is desktop: '))

deskpath = "C:\\Users\\Donald\\Desktop\\"

inputewfolder = deskpath+inputewfolder
inputmoog = deskpath+inputmoog+'.csv'
feoutput = deskpath+feoutput+'.txt'
alloutput = deskpath+alloutput+'.txt'

contents = os.listdir(inputewfolder)
filepathlist = []
filelistlong = []
for item in contents:
    if ".txt" in item:
        filelistlong.append(item)
        filepathlist.append(inputewfolder+'\\'+item)
        
masternamelist = []
masterwavelist = []
masterelmlist = []
masterewlist = []
masterabundlist = []

#generates list of stars in the moog ew input files (X.xxxx format, no bin/rot)
moogstarlist = []
for line in filelistlong:
    newstring = line.replace('.txt', '')
    moogstarlist.append(newstring)

#definitely some unecessary opening/closing of files here, but should only be 
#on the order of 10-100.
for line in range(len(moogstarlist)):
    moogstarname = moogstarlist[line]
    currentstar = open(filepathlist[line], 'r')
    #reads in each moog ew input line by line into list, strips out title line
    mooglines = currentstar.readlines()
    mooglines = mooglines[1:]
    moogwavelist = []
    moogewlist = []
    for entry in mooglines:
        currentline=entry
        templist = currentline.split()
        moogwavelist.append(templist[0])
        moogewlist.append(templist[5])
    #at this point, have a single star's ews and waves from moog file stored 
    #into lists. now time to manipulate the line by line abund sheet
    spreadsheet = open(inputmoog, 'r')
    spreadsheetlines = spreadsheet.readlines()
    titleline = spreadsheetlines[0]
    spreadsheetlines=spreadsheetlines[1:]
    #splits along tabs
    titleline = titleline.split('\t')
    titlelinetrim = []
    #removes trailing newline, rot, bin flags, stores into new list (newline 
    #strip removes in original list too)
    for entry in range(len(titleline)):
        tempentry = titleline[entry]
        tempentry = tempentry.strip('\n')
        titleline[entry] = tempentry
        tempentry = tempentry.strip('bin')
        tempentry = tempentry.strip('rot')
        titlelinetrim.append(tempentry)
    #now matches the current moog star with entry in title line of all abunds,
    #stores that index as the key to pick out the abundances for each line
    for star in range(len(titlelinetrim)):
        allstarname = titlelinetrim[star]
        key = 0
        allelmlist=[]
        allwavelist=[]
        abundlist=[]
#passed up to here: matches stars correctly
        if allstarname == moogstarname:
            #found a match, now it actually constructs lists of ews, etc for the star
            key = star
            sortedmoogew = []
            for line in spreadsheetlines:
                currentline = line
                currentline = currentline.split('\t')
                for entry in range(len(currentline)):
                    tempentry = currentline[entry]
                    tempentry = tempentry.strip('\n')
                    currentline[entry]=tempentry
                allwavelist.append(currentline[0])
                allelmlist.append(currentline[1])
                abundlist.append(currentline[key])
                #now has abunds, elms, waves from abund csv in lists
                #need to double check sort on ew file
            for allwave in range(len(allwavelist)):
                if allwavelist[allwave] in moogwavelist:  
                    for moogwave in range(len(moogwavelist)):
                        if allwavelist[allwave] == moogwavelist[moogwave]:
                            sortedmoogew.append(moogewlist[moogwave])
                        else:
                            snakes = 2
                else:
                    sortedmoogew.append('')
            #confirmed that list of ews is sorted correctly
            for index in range(len(allwavelist)):
                masternamelist.append(titleline[star])
                masterwavelist.append(allwavelist[index])
                masterelmlist.append(allelmlist[index])
                masterewlist.append(sortedmoogew[index])
                masterabundlist.append(abundlist[index])
        else:
            snakes=2
    currentstar.close()
    spreadsheet.close()

#great, all done. now output files. makes one with just fe values first:
feout = open(feoutput, 'w')
feout.write('star line element ew a(fe)'+ '\n')
for element in range(len(masterwavelist)):
    if masterelmlist[element] == 'Fe':
        feout.write(str(masternamelist[element])+' '+str(masterwavelist[element])+' '+str(masterelmlist[element])+' '+str(masterewlist[element])+' '+str(masterabundlist[element])+'\n')
    else:
        snakes=3
allout = open(alloutput, 'w')
allout.write('star line element ew a(x)'+ '\n')
for element in range(len(masterwavelist)):
    allout.write(str(masternamelist[element])+' '+str(masterwavelist[element])+' '+str(masterelmlist[element])+' '+str(masterewlist[element])+' '+str(masterabundlist[element])+'\n')

feout.close()
allout.close()
            
            
    