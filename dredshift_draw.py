#basically same as d4000 code, except only monte carlos the redshifts - no d4000 work at all
__author__ = 'donald'
import numpy as np
import os
import time
import math
from numpy import random as rn
from scipy.interpolate import interp1d
from astropy.io import fits
import multiprocessing

def specpars(filename,redshiftfile): #temp function that parses 1D 3D-HST spectra, hands off to error function
#be sure to pass it the full path+name of the target spectrum
#will need to replace with a 2D optimal extraction function eventually
#ask greg about sensitivity correction (using sensitivity column)
#ask iva about whether or not i should be doing sensitivity corrections
#if so, would also correct the error with the sensitivity as well
    iserror=False
    image=fits.open(filename)
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
    for entry in range(len(flux)):
        flux[entry]=flux[entry]-contamination[entry]
        flux[entry]=flux[entry]/sensitivity[entry]
    if len(flux)!=len(wavelength):
        iserror=True
    elif len(error)!=len(wavelength):
        iserror=True
    elif len(error)!=len(flux):
        iserror=True
    #slices up redshift probability file
    zprobs=fits.open(redshiftfile)
    redshifts=np.array(zprobs[3].data)
    oprobabilities=np.array(zprobs[4].data)
    return{'wavelength':wavelength,'flux':flux,'error':error,'redshifts':redshifts,'o_probabilities':oprobabilities,'iserror':iserror}

def rshift_draw(redshifts,oprobabilities,flag,smoothprob,smoothred,flag2): #handles redshifting d4k indices
    #converts from ln(prob, redshift) to linear values
    iserror=False
    probabilities=[]
    rn.seed()
    grizm='-99'
    for entry in range(len(redshifts)):
        probabilities.append((oprobabilities[entry])) #STILL TRUE
    if flag:
        if flag2: #only interpolates once per galaxy to speed up code-flag2 controls this
            for entry in range(len(redshifts)):
                redshifts[entry]=math.log(redshifts[entry]+1)
            smoothred=np.linspace(min(redshifts),max(redshifts),num=10*len(redshifts))
            interp_prob=interp1d(redshifts,probabilities,kind='linear')
            #normalizes the probability distribution to sum to 1.0
            smoothprob=interp_prob(smoothred)
            for entry in range(len(smoothred)):
                smoothred[entry]=math.exp(smoothred[entry])-1
            normalization=sum(smoothprob)/10
            for entry in range(len(smoothprob)):
                smoothprob[entry]=smoothprob[entry]/(10*normalization)
            #draws redshift using given probabilities and np.random.choice (sampling with replacement)
            zdrawn=np.random.choice(smoothred,p=abs(smoothprob)) #abs value - removes negative floating point errors
            grizm=zdrawn
        else:
            zdrawn=np.random.choice(smoothred,p=abs(smoothprob))
            grizm=zdrawn
    #here returns the maximally likely redshift without interpolation for calculating measured d4000
    if not flag:
        zdrawn=0.0
        maximal=max(probabilities)
        for entry in range(len(redshifts)):
            if probabilities[entry]==maximal:
                zdrawn=redshifts[entry]
                grizm=redshifts[entry]
    if zdrawn==0.0:
        iserror=True
    return{'smp':smoothprob,'smr':smoothred,'iserror':iserror,'grizm':grizm}

def per_gal_d4k(filename, zfilename): #calls previous functions, etc. to return d4k + unc for a single galaxy, and flags
    errflags=''
    parse=specpars(filename,zfilename)
    if parse['iserror']:
        errflags+='Y'
    else:
        errflags+='n'
    flag=False #Flag to indicate whether or not to draw for d4k or use measured values
    flag2=True #flag to tell rshift draw to interpolate to smooth redshift prob grid
    keepgoing=True #flag to indicate whether or not to proceed with MC. False if cannot get measured d4k
    iterations=3001 #monte carlo iterations +1 for measured loop (3000 after noting 1000 not stable always)
    smoothprob=[]
    smoothred=[]
    unc_red_high=-99
    unc_red_low=-99
    unc_redhigh95=-99
    unc_redlow95=-99
    unc_redhigh99=-99
    unc_redlow99=-99
    #added to be able to calculate redshift 68% intervals
    redshiftlist=[]
    for entry in range(iterations):
        if entry>=1: #don't reinterpolate redshift if greater than first iteration
            flag=True
        if not flag:
            reds=rshift_draw(parse['redshifts'],parse['o_probabilities'],flag,smoothprob,smoothred,flag2)
            if reds['iserror']:
                errflags+='Y'
            else:
                errflags+='n'
                grism_z=reds['grizm']
                errflags+='n'
        elif keepgoing and flag: #monte carlo work
            reds=rshift_draw(parse['redshifts'],parse['o_probabilities'],flag,smoothprob,smoothred,flag2)
            redshiftlist.append(reds['grizm'])
            smoothprob=reds['smp']
            smoothred=reds['smr']
            flag2=False
    if keepgoing: #if passes all previous flags, then will go ahead and output statistics and a few other flag options
        redshiftlist=sorted(redshiftlist)
        redhigh=[]
        redlow=[]
        redhigherr=[]
        redlowerr=[]
        redhigh95=[]
        redhigh99=[]
        redlow95=[]
        redlow99=[]
        unc_red_high='-99'
        unc_red_low='-99'
        unc_redhigh95='-99'
        unc_redlow95='-99'
        unc_redhigh99='-99'
        unc_redlow99='-99'
        for entry in range(len(redshiftlist)):
            redshiftlist[entry]=float(redshiftlist[entry])-float(grism_z)
            if redshiftlist[entry]>0.0:
                redhigh.append(redshiftlist[entry])
            elif redshiftlist[entry]<0.0 and redshiftlist[entry]>-50.0:
                redlow.append(redshiftlist[entry])
        for entry in range(len(redhigh)):
            if float(entry+1)/float(len(redhigh))<0.68:
                redhigherr.append(redhigh[entry])
            if float(entry+1)/float(len(redhigh))<0.95:
                redhigh95.append(redhigh[entry])
            if float(entry+1)/float(len(redhigh))<0.99:
                redhigh99.append(redhigh[entry])
        for entry in range(len(redlow)):
            if float(entry+1)/float(len(redlow))>0.32:
                redlowerr.append(redlow[entry])
            if float(entry+1)/float(len(redlow))>0.05:
                redlow95.append(redlow[entry])
            if float(entry+1)/float(len(redlow))>0.01:
                redlow99.append(redlow[entry])
        if len(redhigherr)!=0:
            unc_red_high=abs(redhigherr[-1])
        if len(redlowerr)!=0:
            unc_red_low=abs(redlowerr[0])
        if len(redhigh95)!=0:
            unc_redhigh95=abs(redhigh95[-1])
        if len(redlow95)!=0:
            unc_redlow95=abs(redlow95[0])
        if len(redhigh99)!=0:
            unc_redhigh99=abs(redhigh99[-1])
        if len(redlow99)!=0:
            unc_redlow99=abs(redlow99[0])
    return([errflags,grism_z,unc_red_high,unc_red_low,unc_redhigh95,unc_redlow95,unc_redhigh99,unc_redlow99])

#multicore implementation
def multicore(filenames,zfilenames,processcount): #parallelization function - assigns subsets of galaxies to processes
    def worker(filenames,zfilenames,output):
        outputdict={}
        for entry in range(len(filenames)): #gonna need to search through folder, match zfile and spect file lists
            galaxy=filenames[entry].split('.')
            galaxy=galaxy[0]
            outputdict[galaxy]=per_gal_d4k(filenames[entry],zfilenames[entry])
        output.put(outputdict)
    output=multiprocessing.Queue()
    subset=int(math.ceil(len(filenames)/float(processcount)))
    procs=[]
    for i in range(processcount):
        p=multiprocessing.Process(target=worker,args=(filenames[subset*i:subset*(i+1)],zfilenames[subset*i:subset*(i+1)],output))
        procs.append(p)
        p.start()
    results={}
    for i in range(processcount):
        results.update(output.get())
    for p in procs:
        p.join()
    return(results)

def Wrapper(): #wraps up everything and includes the I/O
    #simple search ability to get filenames from current directory - pretty hardcoded here
    outputname=str(raw_input('output file name, path is current dir: '))
    outputname=outputname+'.csv'
    spectrakey1=str('IRC0218A-G102_')
    spectrakey2=str('1D.fits')
    pzkey1=str('multifit.pz.fits')
    filename=[]
    zfilename=[]
    contents=os.listdir('./') #just runs through directory the script is placed in
    start_time = time.time()
    for entry in range(len(contents)):
        if spectrakey1 in contents[entry] and spectrakey2 in contents[entry]:
            filename.append(contents[entry])
            splitit=contents[entry].split('.')
            tempsplit=splitit[0].split('_')
            pzkey2='_JOIN_'+tempsplit[1]
            for entry2 in range(len(contents)):
                if pzkey1 in contents[entry2] and pzkey2 in contents[entry2]:
                    zfilename.append(contents[entry2])
            if len(filename)!=len(zfilename): #removes spectra if no pz file
                del filename[-1]
    processcount=multiprocessing.cpu_count()
    results=multicore(filename,zfilename,processcount)
    filewrite=open(outputname,'w')
    filewrite.write('\nname'+'\t'+'grism_z'+'\t'+'unc_redhigh68'+'\t'+'unc_redlow68'+'\t'+'unc_redhigh95'+'\t'+'unc_redlow95'+'\t'+'unc_redhigh99'+'\t'+'unc_redlow99'+'\t'+'flag'+'\n')
    for key,entry in results.items():
        filewrite.write(str(key)+'\t'+'\t'+str(entry[1])+'\t'+str(entry[2])+'\t'+str(entry[3])+'\t'+str(entry[4])+'\t'+str(entry[5])+'\t'+str(entry[6])+'\t'+str(entry[7])+'\t'+str(entry[0])+'\n')
    filewrite.close()
    elapsed_time = time.time() - start_time
    print("Executed in "+str(elapsed_time)+"s")

Wrapper()
