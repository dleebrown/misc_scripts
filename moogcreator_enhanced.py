# -*- coding: utf-8 -*-
#
#MOOGCREATOR
#Author: Donald Lee-Brown
#Updated: 03/21/2015
#
#generates moog param files, given a linelist (sameish format as eqwgrabber) and a spreadsheet of collated eqws
#in csv form
#eqw sheet should be format of eqwgrabber script, BUT remove the wavelength and species columns, and leave the
#title column. will output completed moog param files with title same as eqwgrabber script outputs in specified folder

#FOR THIS TO WORK: NEED THE LINELIST WITH TWO EXTRA APPENDED COLUMNS CALLED 'AN' THAT HAS ATOMIC NUMBER AND ONE WITH 'loggf' with TWEAKED loggf vals
#AND ALSO NEED TO SORT BOTH THE EQW SHEET AND THE LINELIST BY THIS NUMBER (ASCENDING)
#also make sure ew sheet and moogready list have the same number of lines (e.g. same 5 iron lines, etc)
#ALSO NEED TO FIX THE NUMBER OF DIGITS IN EACH TEXT COLUMN - XX.X FOR ATOMIC NUMBERS
#XXX.XX FOR EQUIVALENT WIDTHS, XXXX.XX FOR WAVELENGTHS, X.XX FOR EXCITATION POTS, X.XXX FOR TWEAKED LOGGF
#can do this in calc: cell>format>user defined - set format in box at bottom i.e 0.00
#added 02/06/15, updated 03/21/15
#3 options, basic,enhanced, and experimental.
#basic functions as noted above
#enhanced makes some provision for masking out additional lines based on noise levels and calculated SNRs
#experimental accounts for a varying SNR across the spectrum, and directly uses the robospect error
#-------------------------------------------------------------------------------------------------------------------------------
#basic moogcreator as originally written - merely takes lines with eqws greater than zero, loggfs, etc, and packages nice little 
#moog input files for each star in the target folder. 
def Basic_Moogcreator(inputeqw, inputlist,outputfolder):  

    wavelist = []
    excitelist = []
    elmlist = []
    ionlist = []
    atomnum = []
    loggf = []
    
    robolist = open(inputlist, 'r')
    for line in robolist:
        snakes=line.replace("'",'')
        snakes=snakes.split()
        wavelist.append(snakes[0])
        excitelist.append(snakes[1])
        elmlist.append(snakes[2])
        ionlist.append(snakes[3])
        atomnum.append(snakes[4])
        loggf.append(snakes[5])
    
    wavelist = wavelist[1:]
    excitelist = excitelist[1:]
    elmlist = elmlist[1:]
    ionlist = ionlist[1:]
    atomnum = atomnum[1:]
    loggf = loggf[1:]
    
    eqws = open(inputeqw, 'r')
    
    names = eqws.readline()
    names = names.split()
    
    #if there's a standard moog header, now would be the time
    for subline in range(len(names)):
        temp3 = open(outputfolder+'\\'+names[subline]+'.txt', 'w')
        temp3.write(names[subline]+'\n')
        temp3.close()
    
    tally = 0
    tally2 = 0
    for line in range(len(wavelist)):
        temp = eqws.readline()
        temp = temp.split()
        for subline in range(len(names)):   
            #will need to define the rest of the string to append
            temp2 = open(outputfolder+'\\'+names[subline]+'.txt', 'a')
            mango = []
            if float(temp[subline])>0:
                tally2 = tally2+1
                q = wavelist[line]
                w = atomnum[line]
                e = excitelist[line]
                r = loggf[line]
                mango.append('  '+q+'    '+w+'        '+e+'     '+r+'       '+'2.2'+'                '+temp[subline])
                temp2.write(mango[0]+'\n') 
                temp2.close()
                mango = []
            else:
                tally = tally + 1
                tally2=tally2+1
                gotcha = 'total lines discarded:'+' '+str(tally)
                temp2.close()
                
    print(gotcha)
    measured = 'lines measured:'+' '+str(tally2)
    print(measured)
    fraction = float(tally)/float(tally2)
    good = 'fraction lines discarded:'+' '+str(fraction)
    print(good)
    return()
#-------------------------------------------------------------------------------------------------------------------------------
#Enhanced moogcreator: adds masking ability based on SNR and significance of measurement. Essentially the same as vanilla moogcreator,
#except takes in snrgrabber output as well. From there, Cayrell 1988 expected width errors are calculated for each star. Then, when
#generating moog inputs, the program will also mask any lines with eqws < 3sigma from being consistent with zero, as well as 
#removing lines with negative eqws. Statistics on the cuts to each line are kept written to a file. 
def Enhanced_Moogcreator(inputeqw, inputlist,outputfolder,inputsnrs,outputstats):
    
    wavelist = []
    excitelist = []
    elmlist = []
    ionlist = []
    atomnum = []
    loggf = []
    snrsnames =[]
    snrs = []
    snrslist = open(inputsnrs, 'r')
    for line in snrslist:
        monkeys=line
        monkeys=monkeys.split()
        name=monkeys[0]
        name = name.split('_')
        snrsnames.append(name[0])
        snrs.append(monkeys[1])
              
    robolist = open(inputlist, 'r')
    for line in robolist:
        snakes=line.replace("'",'')
        snakes=snakes.split()
        wavelist.append(snakes[0])
        excitelist.append(snakes[1])
        elmlist.append(snakes[2])
        ionlist.append(snakes[3])
        atomnum.append(snakes[4])
        loggf.append(snakes[5])
    
    wavelist = wavelist[1:]
    excitelist = excitelist[1:]
    elmlist = elmlist[1:]
    ionlist = ionlist[1:]
    atomnum = atomnum[1:]
    loggf = loggf[1:]
    
    tallylist = [] #sets up list to count rejections for each line
    for item in range(len(wavelist)):
        tallylist.append(0.00)
        
    eqws = open(inputeqw, 'r')
    names = eqws.readline()
    names = names.split()
    
    #if there's a standard moog header, now would be the time
    for subline in range(len(names)):
        temp3 = open(outputfolder+'\\'+names[subline]+'.txt', 'w')
        temp3.write(names[subline]+'\n')
        temp3.close()
    
    tally = 0
    tally2 = 0
    for line in range(len(wavelist)):
        temp = eqws.readline()
        temp = temp.split()
        for subline in range(len(names)):   
            #will need to define the rest of the string to append
            temp2 = open(outputfolder+'\\'+names[subline]+'.txt', 'a')
            mango = []
            starsnr = 0
            counter=1
            for entry in range(len(snrsnames)):               
                if snrsnames[entry]==names[subline]:
                    #calculation of error in EW using cayrel 88 and assumed instrumental parameters
                    starsnr = float(snrs[entry])
                    starsnr = 480.0/starsnr
                else: #catches stars with no match btw SNR and EWs
                    counter = counter+1
                if counter > len(snrsnames):
                    print("warning, cannot match star "+str(names[subline])+' EWs and SNR')
                    return()
            if (float(temp[subline])-float(3*starsnr))>0 and float(temp[subline])<200.0: #same as before, but applies 3sig and <200
                tally2 = tally2+1
                q = wavelist[line]
                w = atomnum[line]
                e = excitelist[line]
                r = loggf[line]
                mango.append('  '+q+'    '+w+'        '+e+'     '+r+'       '+'2.2'+'                '+temp[subline])
                temp2.write(mango[0]+'\n') 
                temp2.close()
                mango = []    
            else:
                tally = tally + 1
                tally2 = tally2+1
                tallylist[line]=tallylist[line]+1
                gotcha = 'total lines discarded:'+' '+str(tally)
                temp2.close()
#prints an output file with line by line discard statistics            
    output=open(outputstats,'w')
    output.write('wavelength element discarded fracdiscard \n')
    for line in range(len(wavelist)):
        wa=wavelist[line]
        el=elmlist[line]
        re=tallylist[line]
        fr=tallylist[line]/len(names)
        output.write(str(wa)+' '+str(el)+' '+str(re)+' '+str(fr)+'\n')
    output.close()   
    print(gotcha)
    measured = 'lines measured:'+' '+str(tally2)
    print(measured)
    fraction = float(tally)/float(tally2)
    good = 'fraction lines discarded:'+' '+str(fraction)
    print(good)
    return()        
#-------------------------------------------------------------------------------------------------------------------------------
#Experimental moogcreator: adds masking ability based entirely on robospect outputs. Rather than using the robospect-derived
#error to calculate an SNR and using the Cayrell process, this script uses the robospect error estimate
#and the best-fit continuum estimate to ensure that lines being fitted are at least 3-sigma in 
#significance - this is actually somewhat nice because we have naive 3-sigma line finding turned on in
#robospect - so now all lines in the spectrum are being held to the 3-sigma criterion. 
#as such, this mode requires a folder of .robospect.txt files (turn to .txt using handy trick)
#Statistics on the cuts to each line are kept written to a file. 
#note that this version takes forever to run for some reason (~1 min)
#another note: 03/21/15: looks good so far, but it's difficult to solve the 6609 complex problem,
#where the significance checking routine just uses the larger line's significance for both lines
def Experimental_Moogcreator(inputeqw,inputlist,outputfolder,inputfolder,outputstats):   
    wavelist = []
    excitelist = []
    elmlist = []
    ionlist = []
    atomnum = []
    loggf = []
    contents=os.listdir(inputfolder)
    filepathlist=[]
    filelistlong=[]
    starfilelist=[]
    for line in contents:
        if ".robospect" in line:
            filelistlong.append(line)
            filepathlist.append(inputfolder+'\\'+line)
            temp=line.split('_')
            name=temp[0]
            starfilelist.append(name)
    robolist = open(inputlist, 'r')
    for line in robolist:
        snakes=line.replace("'",'')
        snakes=snakes.split()
        wavelist.append(snakes[0])
        excitelist.append(snakes[1])
        elmlist.append(snakes[2])
        ionlist.append(snakes[3])
        atomnum.append(snakes[4])
        loggf.append(snakes[5])
    
    wavelist = wavelist[1:]
    excitelist = excitelist[1:]
    elmlist = elmlist[1:]
    ionlist = ionlist[1:]
    atomnum = atomnum[1:]
    loggf = loggf[1:]
    
    tallylist = [] #sets up list to count rejections for each line
    for item in range(len(wavelist)):
        tallylist.append(0.00)
        
    eqws = open(inputeqw, 'r')
    names = eqws.readline()
    names = names.split()
    
    #if there's a standard moog header, now would be the time
    for subline in range(len(names)):
        temp3 = open(outputfolder+'\\'+names[subline]+'.txt', 'w')
        temp3.write(names[subline]+'\n')
        temp3.close()
    
    tally = 0
    tally2 = 0
    for line in range(len(wavelist)):
        temp = eqws.readline()
        temp = temp.split()
        for subline in range(len(names)):   
            #will need to define the rest of the string to append
            temp2 = open(outputfolder+'\\'+names[subline]+'.txt', 'a')
            mango = []
            starsnr = 0
            counter=1
            robowave=[]
            robocont=[]
            roboerr=[]
            roboflux=[]
            for entry in range(len(starfilelist)):               
                if starfilelist[entry]==names[subline]:
                    getfile=filepathlist[entry]
                    temp3=open(getfile,'r')
                    for l in temp3:
                        templine=l.split()
                        robowave.append(templine[0])
                        robocont.append(templine[3])
                        roboerr.append(templine[2])
                        roboflux.append(templine[1])
                    temp3.close()
                    robowave=robowave[2:]
                    robocont=robocont[2:]
                    roboerr=roboerr[2:]
                    roboflux=roboflux[2:]
                else: #catches stars with no match btw SNR and EWs
                    counter = counter+1
                if counter > len(starfilelist):
                    print("warning, cannot match star "+str(names[subline])+' EWs and robospect file')
                    return()
            #now need to generate the condition for actually holding onto lines based on robo error
            #goes through robowave list, finds the closest wavelength to linelist wavelength, gets
            #average error in 3 angstrom range, gets the line centroid and calculates significance 
            #from the continuum found by robospect
            for e in range(len(robowave)):
                robowave[e]=float(robowave[e])
                robocont[e]=float(robocont[e])
                roboerr[e]=float(roboerr[e])
                roboflux[e]=float(roboflux[e])
            r_loc=0.0
            l_loc=wavelist[line]
            forwardticker=0.0
            backwardticker=0.0
            ticker=0
            for robowavelength in range(len(robowave)):
                if ticker==0:
                    forwardticker=robowave[robowavelength]-float(l_loc)
                    backwardticker=float(l_loc)-robowave[robowavelength]
                    if forwardticker>backwardticker:
                        r_loc=robowave[robowavelength]
                        ticker=robowavelength                   
            array=[ticker-4,ticker-3,ticker-2,ticker-1,ticker,ticker+1,ticker+2,ticker+3,ticker+4]
            contlist=[]
            errlist=[]
            fluxlist=[]
            for i in array:
                contlist.append(robocont[i])
                errlist.append(roboerr[i])
                fluxlist.append(roboflux[i])
            r_continuum=np.mean(contlist) 
            r_error=np.mean(errlist)
            for i2 in range(len(fluxlist)):
                fluxlist[i2]=abs((fluxlist[i2]-r_continuum)/r_error)
            sigma=float(max(fluxlist))
            if sigma>3.0 and float(temp[subline])<150.0 and float(temp[subline])>0.0: #same as before, but applies 3sig and <150
                tally2 = tally2+1
                q = wavelist[line]
                w = atomnum[line]
                e = excitelist[line]
                r = loggf[line]
                mango.append('  '+q+'    '+w+'        '+e+'     '+r+'       '+'2.2'+'                '+temp[subline])
                temp2.write(mango[0]+'\n') 
                temp2.close()
                mango = []    
            else:
                tally = tally + 1
                tally2 = tally2+1
                tallylist[line]=tallylist[line]+1
                gotcha = 'total lines discarded:'+' '+str(tally)
                temp2.close()
#prints an output file with line by line discard statistics            
    output=open(outputstats,'w')
    output.write('wavelength element discarded fracdiscard \n')
    for line in range(len(wavelist)):
        wa=wavelist[line]
        el=elmlist[line]
        re=tallylist[line]
        fr=tallylist[line]/len(names)
        output.write(str(wa)+' '+str(el)+' '+str(re)+' '+str(fr)+'\n')
    output.close()   
    print(gotcha)
    measured = 'lines measured:'+' '+str(tally2)
    print(measured)
    fraction = float(tally)/float(tally2)
    good = 'fraction lines discarded:'+' '+str(fraction)
    print(good)
    return()        
#-------------------------------------------------------------------------------------------------------------------------------
#program control       
def Main():    
    import os    
    inputeqw=str(raw_input('Input eqw sheet, path is desktop: '))
    inputlist = str(raw_input('Linelist modified used, path is desktop: '))
    output=str(raw_input('Output folder, path is desktop: '))
    deskpath = "C:\\Users\\Donald\\Desktop\\"
    outputfolder = deskpath+output
    os.makedirs(outputfolder)
    inputeqw = deskpath+inputeqw+'.csv'
    inputlist = deskpath+inputlist+'.csv'    
    modeinquire=str(raw_input('mode:"basic" or "enhanced" or "experiment": '))
    if modeinquire=='basic':
        print('basic mode')
        Basic_Moogcreator(inputeqw, inputlist,outputfolder)
        return()        
    elif modeinquire=='enhanced':
        print('enhanced mode')
        inputsnrs=str(raw_input('Input snrs .txt, path is desktop: '))
        outputstats=str(raw_input('Output line statistics, path is desktop: '))
        inputsnrs=deskpath+inputsnrs+'.txt'
        outputstats=deskpath+outputstats+'.txt'
        Enhanced_Moogcreator(inputeqw, inputlist,outputfolder,inputsnrs,outputstats)
        return()
    elif modeinquire=='experiment':
        print('experimental mode')
        import numpy as np
        inputfolder=str(raw_input('input folder of .robospect files, path is desktop: '))
        inputfolder=deskpath+inputfolder
        outputstats=str(raw_input('Output line statistics, path is desktop: '))
        outputstats=deskpath+outputstats+'.txt'
        Experimental_Moogcreator(inputeqw,inputlist,outputfolder,inputfolder,outputstats)
        return()        
    else: 
        print('incorrect mode selection')
        return()
#-------------------------------------------------------------------------------------------------------------------------------
#program
Main()