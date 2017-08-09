# -*- coding: utf-8 -*-
#
#MOOGSIFTER
#Author: Donald Lee-Brown
#Updated: 02/07/2014
#
#Processes MOOG output files and organizes data into useful form. Takes in a folder of moog output files of form *.out.txt
#will need to change extension to .txt when in windows using linux files. Also takes in .csv linelist same format as eqwgrabber
#assumes moog outputs are of standard title form (i.e. A.10007.out.txt, C.1214.out.txt)

#Outputs:
#gives a space delimited text file, line by line abundance summary with columns:
#wavelength, element, 10007, 1214, etc.
#NOTE: if wavelength not present in star's moog file, will set that abundance for that star=' '
#SO DO NOT MERGE DELIMITERS WHEN IMPORTING INTO CALC

#Also gives summary for Fe and Ni:
#space delimited text file with columns:
#starname (i.e. A.10007, C.1214), temp, [g], [Fe/H], vt, linesni, avgni, stdni, epslope_fe, rwslope_fe
#(no rwslope for ni in current linelist (new3680))

#can then run bvadder on this output (once converted to csv)

import os

inputfolder=str(raw_input('Input folder, path is desktop: '))
inputlist = str(raw_input('Linelist used, path is desktop: '))
gfeoutputfile = str(raw_input('global fe output name, path is desktop: '))
gnioutputfile = str(raw_input('global ni output name, path is desktop: '))
linebyline = str(raw_input('line by line abundance output, path is desktop: '))

deskpath = "C:\\Users\\Donald\\Desktop\\"
#CHANGE BACK TO JUST DONALD ON LUNA

inputfolder = deskpath+inputfolder
inputlist = deskpath+inputlist+'.csv'
gfeoutputfile = deskpath+gfeoutputfile+'.txt'
gnioutputfile = deskpath+gnioutputfile+'.txt'
linebyline = deskpath+linebyline+'.txt'

contents = os.listdir(inputfolder)
filepathlist = []
filelistlong = []
for item in contents:
    if ".out" in item:
        filelistlong.append(item)
        filepathlist.append(inputfolder+'\\'+item)

filelist = []
for line in filelistlong:
    newstring = line.replace('.out.txt', '')
    filelist.append(newstring)
    
wavelist = []
elmlist = []
robolist = open(inputlist, 'r')
for line in robolist:
    snakes=line.split()
    wavelist.append(snakes[0])
    elmlist.append(snakes[2])

wavelist = wavelist[1:]
elmlist = elmlist[1:]

rowcount = len(filelist)+1

#linebyline abundances
titlestring = ''
titlestring = 'wavelength'+' '+'elm'+' '+titlestring+filelist[0]
filelist2 = filelist[1:]
for entry in filelist2:
    titlestring = titlestring+' '+entry

titlestring = titlestring +'\n'

justlines = open(linebyline, 'w')
justlines.write(titlestring)

for entry in range(len(wavelist)):
    tackon = str(str(wavelist[entry])+' '+str(elmlist[entry]))
    buildme = ''
    for snakes in range(rowcount-1):
        currentiter = open(filepathlist[snakes],'r')
        abund = ' '
        for line in currentiter:
            if wavelist[entry] in line:
                line = line.replace('\n','')
                splitme = line.strip()
                splitme = line.split()
                abund = str(splitme[5])
                abund = abund.strip()+' '
        buildme = buildme+abund
        currentiter.close()
    tackon = tackon+' '+buildme+'\n'
    justlines.write(tackon)

justlines.close()
robolist.close()

#globals - 1 output for Fe, 1 for Ni, gives columns as noted in masterstring assign
masterstringfe = 'starname'+' '+'temp'+' '+'[g]'+' '+'[Fe/H]'+' '+'vt'+' '+'linesfe'+' '+'avgfe'+' '+'stdfe'+' '+'epslope_fe'+' '+'rwslope_fe'+'\n'
masterstringni = 'starname'+' '+'temp'+' '+'[g]'+' '+'[Fe/H]'+' '+'vt'+' '+'linesni'+' '+'avgni'+' '+'stdni'+' '+'epslope_ni'+'\n'

workalotfe = open(gfeoutputfile, 'w')
workalotfe.write(masterstringfe)
workalotfe.close()

workalotni = open(gnioutputfile, 'w')
workalotni.write(masterstringni)
workalotni.close()

snackalotfe = open(gfeoutputfile, 'a')
snackalotni = open(gnioutputfile, 'a')

for snakes in range(rowcount-1):
    currentiter = open(filepathlist[snakes],'r')
    starname = filelist[snakes]
    temp = ['nope']
    gee = ['nope']
    feh = ['nope']
    veeturb = ['nope']
    avgfe = ['nope']
    stdfe = ['nope']
    linesfe = ['nope']
    avgni = ['nope']
    stdni = ['nope']
    linesni = ['nope']
    epslope_fe = ['nope']
    rwslope_fe = ['nope']
    epslope_ni = ['nope']
    fego = False
    nigo = False
    for line in currentiter:
        if '#Kss72:' in line:
            wantthis = line.split(',')
            templine = wantthis[0]
            geeline = wantthis[1]
            fehline = wantthis[2]
            veeturbline = wantthis[3]
            temp = templine.split('=')
            gee = geeline.split('=')
            feh = fehline.split('=')
            veeturb = veeturbline.split('=')
            temp = temp[1]
            gee = gee[1]
            feh = feh[1]
            veeturb = veeturb[1]
            veeturb = veeturb.split()
            veeturb = veeturb[0]
            temp = temp.strip()
            gee = gee.strip()
            feh = feh.strip()
            veeturb = veeturb.strip()
        if 'Abundance Results for Species Fe' in line:
            fego = True
        if fego and 'average abundance' in line:
            wantthis2 = line.split()   
            avgfe = wantthis2[3]
            stdfe = wantthis2[7]
            linesfe = wantthis2[10]
        if fego and 'E.P. correlation' in line:
            alsowant = line.split()
            epslope_fe = alsowant[4]
        if fego and 'R.W. correlation' in line:
            alsowant2 = line.split()
            rwslope_fe = alsowant2[4]
            fego = False
        if fego and 'No statistics done for R.W. trends' in line:
            fego = False
        if 'Abundance Results for Species Ni' in line:
            nigo = True
        if nigo and 'average abundance' in line:
            wantthis3 = line.split()
            avgni = wantthis3[3]
            stdni = wantthis3[7]
            linesni = wantthis3[10]
        if nigo and 'E.P. correlation' in line:
            wantthis4 = line.split()
            epslope_ni = wantthis4[4]
            nigo = False
        if nigo and 'No statistics done for R.W. trends' in line:
            nigo = False
    feline =starname+' '+str(temp)+' '+str(gee)+' '+str(feh)+' '+str(veeturb)+' '+str(linesfe)+' '+str(avgfe)+' '+str(stdfe)+' '+str(epslope_fe)+' '+str(rwslope_fe)+'\n'
    niline =starname+' '+str(temp)+' '+str(gee)+' '+str(feh)+' '+str(veeturb)+' '+str(linesni)+' '+str(avgni)+' '+str(stdni)+' '+str(epslope_ni)+'\n'
    #print(feline)
    #print(niline)
    snackalotfe.write(feline)
    snackalotni.write(niline)
    currentiter.close()

snackalotfe.close()
snackalotni.close()