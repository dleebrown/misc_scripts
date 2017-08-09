# -*- coding: utf-8 -*-
#
#MOPCREATOR
#Author: Donald Lee-Brown
#Updated: 07/18/2014
#
#Generates a folder of "mop" files for a given folder containing a set of input models (modelcreator) and moogfiles (from moogcreator), 
#the file moog prompts you for when you call it, in the proper format.
#Names of files are numeric with a 'bin' tackon for binaries, set up so that moog outputs files in standard form Config.Number (i.e. A.1002 or A.1002bin)
#Also prompts for whether you want moog graphing turned on or off
#
#NOTES: This code is pretty crude, input files must be of a certain form:
#input models must be of the form Config.Number with no file extension specified on Windows (happily, modelcreator should generate this filename scheme) and must have 
#binarity information specified as Config.Numberbin (i.e. A.1002bin) (again, this is easy to do in modelcreator)
#also added in ability to trim 'rot' tag (ie. A.1002rot or A.1002rotbin)
#input moog files must be of form Config.Number.txt with .txt file extension specified on Windows (moogcreator should do this by default)
#the only extra information allowed is the 'r' flag to specify a redo robospect run (i.e. A.1002r.txt)
#
#Also, need to make sure the model name for a star after removing 'bin', 'rot' flag is 
#EXACTLY the same as the moog file name after removing 'r' flag
#
#after this, the recommended route is as follows: stick all the models, moogfiles, and mops in a folder on deneb, navigate to folder, call moog in terminal, start chugging 
#away using the mop numbers, which should be all in the same area in the folder if sorted by name. then run moogsifter, bvadder, etc. 

#Carpal tunnel Donald highly recommends use of the linux terminal trick to remove the .txt extension
#on all the mop files in the output folder before moving to deneb

import os

inputfolder=str(raw_input('Input folder with moog param files and models, path is desktop: '))
outputfolder = str(raw_input('Output folder to contain mop files, path is desktop: '))
wantplot = str(raw_input('Do you want moog to plot as you go? (yes/no): '))

if wantplot == 'yes':
    plot = 2
elif wantplot == 'no':
    plot = 0
else:
    print('WARNING: incorrect plot preference')

deskpath = "C:\\Users\\Donald\\Desktop\\"
inputfolder = deskpath+inputfolder
outputfolder = deskpath+outputfolder

os.makedirs(outputfolder)

contents = os.listdir(inputfolder)
paramnamelong = []
modelname = []

for item in contents:
    if ".txt" in item:
        paramnamelong.append(item)
    else:
        modelname.append(item)  

paramname = []  

for param in paramnamelong:
    newstring = param.replace('.txt', '')
    paramname.append(newstring)

for param in paramnamelong:
    newstring2 = param.replace('.txt','')
    newstring2.split('.')
    newstring2 = newstring2[1]
    if 'r' in newstring2:
        newstring2 = newstring2.replace('r','')
    else:
        newstring2 = newstring2


#writes each file in the output folder

for entry in paramname:
    #can remove other characters from paramname here too to make paramnames and modelnames match:
    if 'r' in entry:
        bananas = entry.replace('r','')
    else:
        bananas = entry
    for entry2 in modelname:
        modeltrim = entry2
        if 'bin' in modeltrim:
            apples = modeltrim.replace('bin','')
        else:
            apples = modeltrim
        if 'rot' in apples:
            apples = apples.replace('rot','')
        else:
            apples = apples
        
        if apples == bananas:
            modeltrimmer = modeltrim.split('.')
            modeltrimmer = modeltrimmer[1]

            #double checks to make sure name is ok!
            apples = apples.split('.')
            apples = apples[1]
            apples = int(apples)
            apples = str(apples)
            
            outfile = outputfolder+'\\'+modeltrimmer+'.txt'
            filetile = open(outfile, 'w')
            workinprogress = []
            workinprogress.append('abfind'+'\n')
            workinprogress.append("standard_out    'out1'"+'\n')
            outstring = str(entry2+'.out')
            workinprogress.append("summary_out     '"+outstring+"'"+'\n')
            workinprogress.append("smoothed_out    'out3'"+'\n')
            workinprogress.append("model_in        '"+entry2+"'"+'\n')
            workinprogress.append("lines_in        '"+entry+'.txt'+"'"+'\n')
            workinprogress.append("molecules    2"+'\n')
            workinprogress.append("lines        3"+'\n')
            workinprogress.append("flux/int     0"+'\n')
            workinprogress.append("damping      0"+'\n')
            workinprogress.append("terminal   x11"+'\n')
            workinprogress.append("plot         "+str(plot))
            for item in workinprogress:
                filetile.write(item)
            filetile.close()
    
contents2 = os.listdir(outputfolder)
if len(contents2) == len(paramname):
    print("output and input folders have the same number of files!")
    notoriginal = str(len(contents2))
    print("Files output: "+notoriginal+'.')
else:
    print("yo, problem: output and input folders don't have the same number of files!")
    original = str(len(paramname))
    notoriginal = str(len(contents2))
    print("Number of output files: "+notoriginal+'. Number of input files: '+original+'.')

    
        