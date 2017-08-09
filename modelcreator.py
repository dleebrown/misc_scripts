# -*- coding: utf-8 -*-
#
#MODELCREATOR
#Author: Donald Lee-Brown
#Updated: 01/15/2014
#
#generates atmospheric models using a tab delimited csv spreadsheet with the following columns:
#outputname, config, temp, logg, posneg (p or m, depending on overall metal abund),initmet, microv
#folder the generated script is run from needs to have the atm directory in it
#dumps as text file

#need to remove stars with incomplete params
#since the models have the filenames to use when making moog templates, it's good to have binaries noted on the input file such that output model file is Config.Numberbin

#NOTE: for some reason this only works correctly with a dummy row of nonsense at bottom of csv columns

#07/13/14: failed to generate model script for first star, had to manually add

import csv

inputfile=str(raw_input('Input name, path is desktop: '))
inputpath="C:\\Users\\Donald\\Desktop\\"
outputfile=str(raw_input('Output name, path is desktop: '))

reading=csv.reader(open(inputpath+inputfile+'.csv','rb'),delimiter='\t')

starnum,config,temp,logg,posneg,initmet, microv = zip(*reading)

numcommands=len(starnum)

path = "./atm/mspawn -w"
for snakes in range(1,numcommands):
    modelscript = path+config[snakes]+'.'+starnum[snakes]+' -t'+temp[snakes]+' -g'+logg[snakes]+' -'+posneg[snakes]+initmet[snakes]+' -v'+microv[snakes]+' \n'
    orange = open(inputpath+outputfile+'.txt','a')
    orange.write(modelscript)
    orange.close()