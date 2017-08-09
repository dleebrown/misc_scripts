# -*- coding: utf-8 -*-
#
#ROBOCREATOR
#Author: Donald Lee-Brown
#Updated: 01/01/2014
#
#ROBOSPECT script generator
#Takes TAB DELIMITED .csv file as input, returns ROBOSPECT script (set up for .fits)
#input should contain columns in this order and name: starnum,aperture,imagenum, roboimagenum,roborad_vel,outputname,config,inputname
#will return robospect routine as text file: robospect -L <linelist> -F -f 3, -M pre, -P <outputname>_<config> <inputname> --fits_row <roboimage#> --rad_vel <roborad_vel> -i 25
#Edited 10/18/2013

import csv

inputfile=str(raw_input('Input name, path is desktop: '))
inputpath="C:\\Users\\Donald\\Desktop\\"
outputfile=str(raw_input('Output name, path is desktop: '))

reading=csv.reader(open(inputpath+inputfile+'.csv','rb'),delimiter='\t')

starnum,aperture,imagenum,roboimagenum,roborad_vel,outputname,config, inputname = zip(*reading)

numcommands=len(roboimagenum)
print(numcommands)

robospect="robospect "
linelist = str(raw_input('Linelistname: '))
linelist ="-L "+linelist+" "
naive = "-F -f 3 "
contfit = "-M pre "
iterate = "-i 25 "
boxcar = "-C boxcar "
width = "-V 20"
#boxcar and width not in output currently

for snakes in range(1,numcommands):
    robocommand = robospect+linelist+naive+contfit+"-P "+config[snakes]+'.'+outputname[snakes]+' '+inputname[snakes]+' '+'--fits_row '+roboimagenum[snakes]+' '+'--radial_velocity '+roborad_vel[snakes]+' '+iterate+'\n'
    orange = open(inputpath+outputfile+'.txt','a')
    orange.write(robocommand)
    orange.close()
    
#orange=open(inputpath+outputfile,'a')
#robocommand = robospect+linelist+naive+contfit+"-P "+outputname[numcommands-1]+'_'+config[numcommands-1]+' '+inputname[numcommands-1]+' '+'--fits_row '+roboimagenum[numcommands-1]+' '+'--radial_velocity '+roborad_vel[numcommands-1]+' '+iterate+'\n'
#orange.write(robocommand)
#orange.close

postscriptkill = "rm *.robo.ps"
orange=open(inputpath+outputfile,'a')
orange.write(postscriptkill+'\n')
orange.close()
print("done")

