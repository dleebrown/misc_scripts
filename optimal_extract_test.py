__author__ = 'donald'

#testing to make sure my 1D optimal extraction is returning the same results as whatever the 3dhst team did
import numpy as np
import os
import time
import math
from numpy import random as rn
from scipy.interpolate import interp1d
from astropy.io import fits
import multiprocessing

def oned_specpars(filename): #temp function that parses 1D 3D-HST spectra, hands off to error function
#be sure to pass it the full path+name of the target spectrum
#will need to replace with a 2D optimal extraction function eventually
#ask greg about sensitivity correction (using sensitivity column)
#ask iva about whether or not i should be doing sensitivity corrections
#if so, would also correct the error with the sensitivity as well
    iserror=False
    image=fits.open(filename)
    image.info()
    imagedata=image[1].data
    wavelength=np.array(imagedata.field(0))
    flux=np.array(imagedata.field(1))
    error=np.array(imagedata.field(2))
    contamination=np.array(imagedata.field(3))
    sensitivity=np.array(imagedata.field(6))
#outputs fits files as text files for debugging - don't uncomment when running on a whole directory
#    writeme=file('output.txt','w')
#    for line in range(len(wavelength)):
#        writeme.write(str(wavelength[line])+' '+str(flux[line])+' '+str(error[line])+' '+str(contamination[line])+' '+'\n')
#    writeme.close()
    if len(flux)!=len(wavelength):
        iserror=True
    elif len(error)!=len(wavelength):
        iserror=True
    elif len(error)!=len(flux):
        iserror=True
    return{'wavelength':wavelength,'flux':flux,'contamination':contamination,'sensitivity':sensitivity,'error':error,'iserror':iserror}

def twod_specpars(filename):
    image=fits.open(filename)
    image.info()
    scidata=image['SCI'].data
    whtdata=image['WHT'].data
    wavedata=image['WAVE'].data
    sendata=image['SENS'].data
    tracedata=image['YTRACE'].data
    contamdata=image['CONTAM'].data
    modeldata=image['MODEL'].data
    return{'wavelength':wavedata,'flux':scidata,'contamination':contamdata,'sensitivity':sendata,'error':whtdata,'trace':tracedata,'model':modeldata}

#function optimally extracts a 2D array with same dimensions as model,error,using weights provided by model and error
def optimal_weights(twod_array,twod_error,twod_model,length):
    extracted=np.zeros((length,1))
    for wavelength in range(length):
        x_model=[]
        sumnumerator=float(0)
        sumdenominator=float(0)
        #need to clean the data first - trim down each x-array such that disregard pixels <10% of peak
        #work on the model: need to insert normalization condition
        for xcoord in range(len(twod_array)):
            if twod_model[xcoord,wavelength]<=0.0:
                twod_model[xcoord,wavelength]=0.0
            x_model.append(twod_model[xcoord,wavelength])
        normalize=sum(x_model)
        for xcoord in range(len(twod_array)):
            x_model[xcoord]=x_model[xcoord]/normalize
        for xcoord in range(len(twod_array)):
            if x_model[xcoord]!=float(0) and twod_error[xcoord,wavelength]!=float(0):
                sumnumerator+=twod_array[xcoord,wavelength]*(x_model[xcoord]/twod_error[xcoord,wavelength]**2)
                sumdenominator+=x_model[xcoord]**2/twod_error[xcoord,wavelength]**2
        if sumdenominator!=float(0):
            extractedflux=sumnumerator/sumdenominator
        else:
            extractedflux=float(0)
        extracted[wavelength,0]=extractedflux
    return(extracted)

def straight_sum(twod_array,twod_error,twod_model,length):
    extracted=np.zeros((length,1))
    for wavelength in range(length):
        summit=sum(twod_array[:,wavelength])
        extracted[wavelength,0]=summit
    return(extracted)

def estraight_sum(twod_array,twod_error,twod_model,length):
    extracted=np.zeros((length,1))
    for wavelength in range(length):
        summit=sum(twod_error[:,wavelength])
        extracted[wavelength,0]=summit
    return(extracted)

#there is a serious problem here with the error output - it doesn't work
def optimal_eweights(twod_array,twod_error,twod_model,length):
    extracted=np.zeros((length,1))
    for wavelength in range(length):
        x_model=[]
        sumnumerator=float(0)
        sumdenominator=float(0)
        #need to clean the data first - trim down each x-array such that disregard pixels <10% of peak
        #work on the model: need to insert normalization condition
        for xcoord in range(len(twod_error)):
            if twod_model[xcoord,wavelength]<=0.0:
                twod_model[xcoord,wavelength]=0.0
            x_model.append(twod_model[xcoord,wavelength])
        normalize=sum(x_model)
        for xcoord in range(len(twod_error)):
            x_model[xcoord]=x_model[xcoord]/normalize
        for xcoord in range(len(twod_error)):
            if x_model[xcoord]!=float(0) and twod_error[xcoord,wavelength]!=float(0):
                sumnumerator+=(x_model[xcoord])
                sumdenominator+=x_model[xcoord]**2/twod_error[xcoord,wavelength]**2
        if sumdenominator!=float(0):
            extractedflux=(sumnumerator/sumdenominator)
        else:
            extractedflux=float(0)
        extracted[wavelength,0]=np.sqrt(extractedflux)
    return(extracted)

def optimal_extract(wave,flux,contam,sense,error,trace,model):
    #will stick stuff in array with columns corresponding to output for oned_specpars
    output_1d=np.zeros((len(wave),6))
    length=len(wave)
    eflux=optimal_weights(flux,error,model,length)
    econtam=optimal_weights(contam,error,model,length)
    #now extracts the error
    eerror=optimal_eweights(flux,error,model,length)
    return{'wave':wave,'flux':eflux,'contam':econtam,'error':eerror,'sense':sense}

def Main():
    #G141 test galaxies
    filename1_oned='/home/donald/Desktop/optimal_test2/uds-18-G141_26108.1D.fits'
    filename1_twod='/home/donald/Desktop/optimal_test2/uds-18-G141_26108.2D.fits'
    filename2_oned='/home/donald/Desktop/optimal_test2/uds-18-G141_29007.1D.fits'
    filename2_twod='/home/donald/Desktop/optimal_test2/uds-18-G141_29007.2D.fits'
    filename3_oned='/home/donald/Desktop/optimal_test2/uds-18-G141_30117.1D.fits'
    filename3_twod='/home/donald/Desktop/optimal_test2/uds-18-G141_30117.2D.fits'
    filename4_oned='/home/donald/Desktop/optimal_test2/uds-18-G141_29841.1D.fits'
    filename4_twod='/home/donald/Desktop/optimal_test2/uds-18-G141_29841.2D.fits'
    filename5_oned='/home/donald/Desktop/optimal_test2/uds-18-G141_31086.1D.fits'
    filename5_twod='/home/donald/Desktop/optimal_test2/uds-18-G141_31086.2D.fits'
    filename6_oned='/home/donald/Desktop/optimal_test2/uds-18-G141_32403.1D.fits'
    filename6_twod='/home/donald/Desktop/optimal_test2/uds-18-G141_32403.2D.fits'
    filename7_oned='/home/donald/Desktop/optimal_test2/uds-18-G141_31745.1D.fits'
    filename7_twod='/home/donald/Desktop/optimal_test2/uds-18-G141_31745.2D.fits'
    filename8_oned='/home/donald/Desktop/optimal_test2/uds-18-G141_33068.1D.fits'
    filename8_twod='/home/donald/Desktop/optimal_test2/uds-18-G141_33068.2D.fits'
    filename9_oned='/home/donald/Desktop/optimal_test2/uds-18-G141_33093.1D.fits'
    filename9_twod='/home/donald/Desktop/optimal_test2/uds-18-G141_33093.2D.fits'
    #G102 test galaxies
    filename10_oned='/home/donald/Desktop/optimal_test2/IRC0218A-G102_29007.1D.fits'
    filename10_twod='/home/donald/Desktop/optimal_test2/IRC0218A-G102_29007.2D.fits'
    filename11_oned='/home/donald/Desktop/optimal_test2/IRC0218A-G102_29841.1D.fits'
    filename11_twod='/home/donald/Desktop/optimal_test2/IRC0218A-G102_29841.2D.fits'
    filename12_oned='/home/donald/Desktop/optimal_test2/IRC0218A-G102_31086.1D.fits'
    filename12_twod='/home/donald/Desktop/optimal_test2/IRC0218A-G102_31086.2D.fits'
    filename13_oned='/home/donald/Desktop/optimal_test2/IRC0218A-G102_32403.1D.fits'
    filename13_twod='/home/donald/Desktop/optimal_test2/IRC0218A-G102_32403.2D.fits'
    filename14_oned='/home/donald/Desktop/optimal_test2/IRC0218A-G102_31745.1D.fits'
    filename14_twod='/home/donald/Desktop/optimal_test2/IRC0218A-G102_31745.2D.fits'
    filename15_oned='/home/donald/Desktop/optimal_test2/IRC0218A-G102_33068.1D.fits'
    filename15_twod='/home/donald/Desktop/optimal_test2/IRC0218A-G102_33068.2D.fits'
    filename16_oned='/home/donald/Desktop/optimal_test2/IRC0218A-G102_33093.1D.fits'
    filename16_twod='/home/donald/Desktop/optimal_test2/IRC0218A-G102_33093.2D.fits'

    firstgal_oned=oned_specpars(filename10_oned)
    firstgal_twod=twod_specpars(filename10_twod)
    optimal=optimal_extract(firstgal_twod['wavelength'],firstgal_twod['flux'],firstgal_twod['contamination'],firstgal_twod['sensitivity'],firstgal_twod['error'],0,firstgal_twod['model'])
    #print(firstgal_oned['wavelength'])
    #which parameter to test optimal vs existing 1d
    test1=firstgal_oned['error']
    test2=optimal['error']
    test3=firstgal_oned['flux']
    #print('existing 1D result:')
    #print(test1)
    #print('optimally extracted result:')
    #print(test2)
    diffarray=[]
    for entry in range(len(test2)):
        diffarray.append(-float(test1[entry])+float(test2[entry]))
    print('(optimally extracted result - existing 1D result)')
    print(diffarray)
    #print(firstgal_oned['sensitivity'])
    print('mean deviation/mean(1D) '+str(np.mean(diffarray)/np.mean(test1)))
    print('median deviation '+str(np.median(diffarray)))
    print('1d mean '+str(np.mean(diffarray)))
    print('max deviation '+str(max(diffarray)))

    print(np.mean(test1))
    print(np.mean(test3)/np.mean(test1))
    #print(firstgal_oned['contamination'])
    #print(firstgal_oned['sensitivity'])
    #print(firstgal_oned['error'])

Main()