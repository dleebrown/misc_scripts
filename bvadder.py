# -*- coding: utf-8 -*-
#temp code, adds in b-v values to a moogsifter global output, 
#takes in space separated csv, outputs txt - takes in spreadsheet with b-v values
#where b-v values are in column 0, starname (numeric) is in column 5
#takes in moogsifter output where star name is in column 0 as A.starname
#compares starnames, if match, then puts b-v value at the beginning of the moogsifter
#file
#works with header columns, but does not work with trailing newlines

msinputfile=str(raw_input('Moogsifter input file, path is desktop: '))
bvinputfile = str(raw_input('b-v input name, path is desktop: '))
outputfile = str(raw_input('output name, path is desktop: '))

deskpath = "C:\\Users\\Donald\\Desktop\\"

msinputfile = deskpath+msinputfile+'.csv'
bvinputfile = deskpath+bvinputfile+'.csv'
outputfile = deskpath+outputfile+'.txt'

msinput = open(msinputfile, 'r')
bvinput = open(bvinputfile, 'r')
output = open(outputfile, 'w')

starlist = []
bvlist = []

for line in bvinput:
    snakes = line.split()
    bv = snakes[0]
    star = snakes[5]
    starlist.append(star)
    bvlist.append(bv)
   
for line in msinput:
    linesplit = line.split()
    littlesplit = linesplit[0]
    if '.' in littlesplit:
        littlesplit = littlesplit.split('.')
        littlesplit = littlesplit[1]
    rawr = line
    for entry in range(len(starlist)):
        if starlist[entry] == littlesplit:
            newstring = str(bvlist[entry])+' '+rawr
            output.write(newstring)
            
    
bvinput.close()
output.close()  
msinput.close()