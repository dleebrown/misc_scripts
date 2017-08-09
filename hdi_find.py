'''
finds the best location for image center on the sky in order to maximise the number of targets in a field (here, the field is HDI)
does this by creating a random half degree field and seeing how many stars fall within
loops for a few thousand iterations, selects the coordinates of the field(s) that minimize(s) the number of pointings needed to cover all the stars
INPUT:
folder of
.csv files with columns KIC, RA, DEC (in degrees)
OUTPUT:
a text file with columns KIC, RA, DEC, POSRA, POSDEC
corresponding to the center coordinate of the field
each subpointing in a one-degree field is separated by a newline, with a double newline between one degree fields

THIS IS NOT SET UP TO HANDLE NEGATIVE DECS
'''

import pandas as pd
import random as rd
import numpy as np
import os

def Main():
    curdir=os.getcwd()
    files=os.listdir(curdir)
    outputfile= open('mlo40_find.out.txt','w')
    iterations=100000
    #cuts about 0.6' off each side in order to avoid truncating the psf
    size=float(0.200)
    outputfile.write('hdi_find_v0.1 iterations:'+str(iterations)+' fieldsize_(deg):'+str(size)+' \n \n')
    for entry in files:
        if '.csv' in entry:
            currentfile=pd.read_csv(entry)
            entry=entry.rstrip('.csv')
            outputfile.write('HYDRA_FIELD_'+str(entry)+' \n')
            names=currentfile['KIC'].values
            ra=currentfile['RA'].values
            dec=currentfile['DEC'].values
            minra=min(ra)
            maxra=max(ra)
            mindec=min(dec)
            maxdec=max(dec)
            #iteratively tries to fit stars in the lowest number of fields, up to 5
            criterion=0
            n_fields=0
            finalfieldcount=0
            while n_fields<=5:
                n_fields+=1
                if criterion<len(names):
                    fields=fieldFinder(names,ra,dec,minra,maxra,mindec,maxdec,size,iterations,n_fields)
                    criterion=fields[5]
                    finalfieldcount=n_fields
            if criterion!=len(names):
                print('warning: may not have found fields for all stars for field '+str(entry))
            stars=fields[0]
            right=fields[1]
            decl=fields[2]
            dista=fields[3]
            fieldce=fields[4]
            outputfile.write('UNIQUE_STARS:'+str(criterion)+'\n \n')
            for f in range(finalfieldcount):
                outputfile.write('HDI_SUBFIELD_'+str(f)+' \n'+'F_COORDS: '+str(fieldce[f,0])+' '+str(fieldce[f,1])+' \n')
                outputfile.write('KIC RA DEC DIST_CENTER \n')
                for i in range(len(stars[f])):
                    outputfile.write(str(stars[f][i])+' '+str(right[f][i])+' '+str(decl[f][i])+' '+str(dista[f][i])+' \n')
                outputfile.write('\n')
            outputfile.write(' \n')
    outputfile.close()

#names, ra, dec are numpy vectors, min/max values are floats, dimension is the field size, iterations, numfields is an int
def fieldFinder(names,ra,dec,minra,maxra,mindec,maxdec,dimension,iterations,numfields):
    #iterates a bunch of times to find random field positions
    fieldcenters=np.ones((numfields,2))
    #metric is the sum of the longest distances from the current fieldcenters to stars in the respective fields
    #for a set of fieldcenters to be superior, they must either encompass more unique stars, or same stars and lower total metric
    metric=200.0
    #count the number of unique stars in the field:
    count=0
    starlist=[[] for i in range(numfields)]
    distances=[[] for i in range(numfields)]
    all_ra=[[] for i in range(numfields)]
    all_dec=[[] for i in range(numfields)]
    for i in range(iterations):
        temp_distances=[[] for i in range(numfields)]
        temp_starlist=[[] for i in range(numfields)]
        temp_ra=[[] for i in range(numfields)]
        temp_dec=[[] for i in range(numfields)]
        center_ra=np.ones((numfields,1))
        center_dec=np.ones((numfields,1))
        for f in range(numfields):
            temp_center_ra=rd.uniform(minra,maxra)
            temp_center_dec=rd.uniform(mindec,maxdec)
            center_ra[f,0]=temp_center_ra
            center_dec[f,0]=temp_center_dec
            for star in range(len(ra)):
                if ra[star]>=temp_center_ra-dimension/2. and ra[star]<=temp_center_ra+dimension/2.:
                    if dec[star]>=temp_center_dec-dimension/2. and dec[star]<=temp_center_dec+dimension/2.:
                        temp_starlist[f].append(names[star])
                        temp_distances[f].append(np.sqrt((temp_center_ra-ra[star])**2+(temp_center_dec-dec[star])**2))
                        temp_ra[f].append(ra[star])
                        temp_dec[f].append(dec[star])
        for f in range(numfields):
            if f==0:
                uniquestars=np.asarray(temp_starlist[f])
            else:
                uniquestars=np.unique(np.concatenate((uniquestars,np.asarray(temp_starlist[f])),0))
        if len(uniquestars)>count:
            tempmetric=0.0
            for f in range(numfields):
                starlist[f]=temp_starlist[f]
                distances[f]=temp_distances[f]
                all_ra[f]=temp_ra[f]
                all_dec[f]=temp_dec[f]
                if len(distances[f])>0:
                    tempmetric+=max(distances[f])
                fieldcenters[f,0]=center_ra[f,0]
                fieldcenters[f,1]=center_dec[f,0]
            count=len(uniquestars)
            metric=tempmetric
        elif len(uniquestars)==count and len(uniquestars)!=0:
            tempmetric=0.0
            for f in range(numfields):
                if len(distances[f])>0:
                    tempmetric+=max(distances[f])
            if tempmetric<metric:
                for f in range(numfields):
                    starlist[f]=temp_starlist[f]
                    distances[f]=temp_distances[f]
                    all_ra[f]=temp_ra[f]
                    all_dec[f]=temp_dec[f]
                    if len(distances[f])>0:
                        tempmetric+=max(distances[f])
                    fieldcenters[f,0]=center_ra[f,0]
                    fieldcenters[f,1]=center_dec[f,0]
                metric=tempmetric
    return(starlist,all_ra,all_dec,distances,fieldcenters,count)

Main()


