# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 11:20:02 2015

@author: Donald
"""

#compares rovets returned by rotvet.py with already calculated ones (from fxcor, for instance)
#need: rotvet.py output (.txt) with c0 to be A.2314 for example. (config.number)
#also: txt file with config in 0, star numbers in column 1, then rotvet in column 2, and then erot in c3, radv in c4, b-v in c5. 
#outputs file with c0=config, c1=starnum, c2=roborot, c3=eroborot, c4=fxrot, c5=efxrot, c6=radv, c7=bv

roborotsf=str(raw_input('robospect rotvet file, path is desktop: '))
fxrotsf = str(raw_input('fxcor rotvets, path is desktop: '))
outputfile = str(raw_input('output name, path is desktop: '))

deskpath = "C:\\Users\\Donald\\Desktop\\"

roborotsf = deskpath+roborotsf+'.txt'
fxrotsf = deskpath+fxrotsf+'.txt'
outputfile = deskpath+outputfile+'.txt'

roborots = open(roborotsf, 'r')
fxrots = open(fxrotsf, 'r')
output = open(outputfile, 'w')

robostarlist = []
roboconfiglist = []
roborotv = []
roboerotv = []

fxstarlist = []
fxconfiglist = []
fxrotv = []
fxerotv = []
fxradv = []
fxbv = []

for line in roborots:
    line = line.split()
    temp = line[0]
    temp = temp.split('.')
    config = temp[0]
    starnum = temp[1]
    rot = line[1]
    erot = line[2]
    robostarlist.append(starnum)
    roboconfiglist.append(config)
    roborotv.append(rot)
    roboerotv.append(erot)

for line in fxrots:
    line = line.split()
    config = line[0]
    starnum = line[1]
    rot = line[2]
    erot = line[3]
    radv = line[4]
    bv = line[5]
    fxstarlist.append(starnum)
    fxconfiglist.append(config)
    fxrotv.append(rot)
    fxerotv.append(erot)
    fxradv.append(radv)
    fxbv.append(bv)

for entry in range(len(robostarlist)):
    for entry2 in range(len(fxstarlist)):
        if fxstarlist[entry2] == robostarlist[entry]:
            string = str(roboconfiglist[entry])+' '+str(robostarlist[entry])+' '+str(roborotv[entry])+' '+str(roboerotv[entry])+' '+str(fxrotv[entry2])+' '+str(fxerotv[entry2])+' '+str(fxradv[entry2])+' '+str(fxbv[entry2])+'\n'
            output.write(string)
        else:
            candycanes = 2 
            
roborots.close()
fxrots.close()
output.close()

