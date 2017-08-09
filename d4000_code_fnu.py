#EDIT 02/29/16: Changed a few filenames/indices to match the JOINT FIT G102 and G141 pz files. abandoned merging in my optimally extraction
#routine, since i have verified that the errors and such are now correct for the updated 1D fits files. Also added in redshift confidence intervals

#EDIT 05/28/16: changed d4000 definition to be fnu instead of flambda, added in more iterations to account for nonstable d4000 errors

#code to measure d4000 in 3d-hst spectra. currently working on 1d version that uses the stacked spectra,
#but will eventually want to bolt on functionality to take care of 2d optimal extraction
#
#iva about stellar mass catalogues for all these galaxies? 3dhst stellar mass data? where to get?
#skelton et al look for coordinates! and other information! before emailing iva
#on 3dhst page - under UDS 
#to get members - take redshift slice
#
#outline of code:
#    1. reads in folder containing relevant images
#    2. extracts important data, performs contamination subtraction, sensitivity correction
#    3. draws a redshift from the redshift distribution, uses redshift information to shift the d4000 indices
#    3a. uses the error information to "draw" the flux in the index region (assuming normal distribution)
#    4. measures d4000
#    5. calculates error using a monte carlo - does X d4000 measures (steps 3-4), redrawing every time, to get a mean d4000+stddev
#    6. writes the result for each star to a master file
import numpy as np
import os
import time
import math
from numpy import random as rn
from scipy.interpolate import interp1d   
from astropy.io import fits 
import multiprocessing

def specpars(filename,redshiftfile): #temp function that parses 1D 3D-HST spectra, hands off to error function
    #ALSO CONVERTS FLAMBDA to FNU AND ELAMBDA TO ENU
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
    c=3.0*(10**8)
    wavelength_m=wavelength/(1.0*(10**(10)))
    nu=c/wavelength_m
#outputs fits files as text files for debugging - don't uncomment when running on a whole directory
#    writeme=file('output.txt','w')
#    for line in range(len(wavelength)):
#        writeme.write(str(wavelength[line])+' '+str(flux[line])+' '+str(error[line])+' '+str(contamination[line])+' '+'\n')
#    writeme.close()
    for entry in range(len(flux)):
        flux[entry]=flux[entry]-contamination[entry]
        flux[entry]=flux[entry]/sensitivity[entry]
        #converts flux to fnu instead of flambda
        flux[entry]=flux[entry]*c/(nu[entry]**2)
    #same conversion for the error
    for entry in range(len(error)):
        error[entry]=error[entry]*c/(nu[entry]**2)
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
        try:
            #linear probs in the new round o data
            probabilities.append(oprobabilities[entry]) #STILL TRUE
        except OverflowError:
            print('offending probability '+str(oprobabilities[entry])+' offending redshift '+str(redshifts[entry]))
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
    #calculates redshifted d4000, dn4000 indices
    i3950=zdrawn*3950.0 + 3950.0
    i3750=zdrawn*3750.0 + 3750.0
    i4250=zdrawn*4250.0 + 4250.0
    i4050=zdrawn*4050.0 + 4050.0
    i3850=zdrawn*3850.0 + 3850.0
    i4100=zdrawn*4100.0 + 4100.0
    i4000=zdrawn*4000.0 + 4000.0
    return{'i39':i3950,'i37':i3750,'i42':i4250,'i40':i4050,'i38':i3850,'i41':i4100,'n40':i4000,'smp':smoothprob,'smr':smoothred,'iserror':iserror,'grizm':grizm}

def flux_draw(wavelength,flux,error,i3950,i3750,i4250,i4050,i3850,i4100,i4000,flag): #handles fluxes within redshifted d4k indices
    (low_f,high_f,low_e,high_e,low_f_n,high_f_n,low_e_n,high_e_n)=([] for i in range(8))
    (low_w,high_w,low_w_n,high_w_n)=([] for i in range (4))
    (n40_w,n40_f,n40_e)=([] for i in range(3)) #creates 50 angstrom array for the 4000-4050 range, for dn4k
    #a positive nancheck or outofbounds will break the function and return error flag
    outofbounds=False
    nancheck=False
    if i3750<min(wavelength) or i4250>max(wavelength):
        outofbounds=True
    if outofbounds:
        return{'error':'outofbounds'}
    for entry in range(len(wavelength)):
        if wavelength[entry]<=float(i3950) and wavelength[entry]>=float(i3750):
            low_w.append(wavelength[entry])
            low_f.append(flux[entry])
            low_e.append(error[entry])
            if math.isnan(wavelength[entry]) or math.isnan(flux[entry]) or math.isnan(error[entry]):
                nancheck=True
        elif wavelength[entry]<=float(i4050) and wavelength[entry]>=float(i4000):
            n40_w.append(wavelength[entry])
            n40_f.append(flux[entry])
            n40_e.append(error[entry])
            if math.isnan(wavelength[entry]) or math.isnan(flux[entry]) or math.isnan(error[entry]):
                nancheck=True
        elif wavelength[entry]<=float(i4250) and wavelength[entry]>=float(i4050):
            high_w.append(wavelength[entry])
            high_f.append(flux[entry])
            high_e.append(error[entry])
            if math.isnan(wavelength[entry]) or math.isnan(flux[entry]) or math.isnan(error[entry]):
                nancheck=True
    if nancheck:
        return{'error':'nancheck'}
    #linearly interpolate flux, error, wavelength at each endpoint: not very efficiently coded right now, change if issue
    low_w_lend=low_w[0]
    low_w_hend=low_w[-1]
    high_w_lend=high_w[0]
    high_w_hend=high_w[-1]
    n40bound=n40_w[0]
    errcheck=0
    for entry in range(len(wavelength)):
        if wavelength[entry]==low_w_lend:
            low_f[0]=(flux[entry]-flux[entry-1])/(wavelength[entry]-wavelength[entry-1])*(i3750-wavelength[entry-1])+flux[entry-1]
            low_e[0]=(error[entry]-error[entry-1])/(wavelength[entry]-wavelength[entry-1])*(i3750-wavelength[entry-1])+error[entry-1]
            low_w[0]=i3750
            errcheck+=1
#PASSED HERE - CALC d4000 disagrees by ~0.001 so likely other interpolations are fine - CHECK NARROW BAND
        elif wavelength[entry]==low_w_hend:
            low_f[-1]=(flux[entry+1]-flux[entry])/(wavelength[entry+1]-wavelength[entry])*(i3950-wavelength[entry+1])+flux[entry+1]
            low_e[-1]=(error[entry+1]-error[entry])/(wavelength[entry+1]-wavelength[entry])*(i3950-wavelength[entry+1])+error[entry+1]
            low_w[-1]=i3950
            errcheck+=1
        elif wavelength[entry]==n40bound:
            n40_f[0]=(flux[entry]-flux[entry-1])/(wavelength[entry]-wavelength[entry-1])*(i4000-wavelength[entry-1])+flux[entry-1]
            n40_e[0]=(error[entry]-error[entry-1])/(wavelength[entry]-wavelength[entry-1])*(i4000-wavelength[entry-1])+error[entry-1]
            n40_w[0]=i4000
            errcheck+=1
        elif wavelength[entry]==high_w_lend:
            high_f[0]=(flux[entry]-flux[entry-1])/(wavelength[entry]-wavelength[entry-1])*(i4050-wavelength[entry-1])+flux[entry-1]
            high_e[0]=(error[entry]-error[entry-1])/(wavelength[entry]-wavelength[entry-1])*(i4050-wavelength[entry-1])+error[entry-1]
            high_w[0]=i4050
            errcheck+=1
        elif wavelength[entry]==high_w_hend:
            high_f[-1]=(flux[entry+1]-flux[entry])/(wavelength[entry+1]-wavelength[entry])*(i4250-wavelength[entry+1])+flux[entry+1]
            high_e[-1]=(error[entry+1]-error[entry])/(wavelength[entry+1]-wavelength[entry])*(i4250-wavelength[entry+1])+error[entry+1]
            high_w[-1]=i4250
            errcheck+=1
    if int(errcheck)!=5:
        print('error in interpolation, errcheck value='+str(errcheck))
    #draw from each error array now, add to the flux arrays of same name (self-update), inits if already calc'd measured d4k
    if flag:
        for item in range(len(low_f)):
            std=abs(low_e[item])
            errorfactor=rn.normal(0.0,std)
            low_f[item]=low_f[item]+errorfactor
        for item in range(len(high_f)):
            std=abs(high_e[item])
            errorfactor=rn.normal(0.0,std)
            high_f[item]=high_f[item]+errorfactor
        for item in range(len(n40_f)):
            std=abs(n40_e[item])
            errorfactor=rn.normal(0.0,std)
            n40_f[item]=n40_f[item]+errorfactor
    #now create narrow ranges for the d4kn index (using same drawn data)
    for entry in range(len(low_w)):
        if low_w[entry]<=float(i3950) and low_w[entry]>=float(i3850):
            low_f_n.append(low_f[entry])
            low_w_n.append(low_w[entry])
    for entry in range(len(n40_f)):
        high_f_n.append(n40_f[entry])
        high_w_n.append(n40_w[entry])
    for entry in range(len(high_w)):
        if high_w[entry]>=float(i4050) and high_w[entry]<=float(i4100):
            high_f_n.append(high_f[entry])
            high_w_n.append(high_w[entry])
    #here interpolation occurs after redrawing error, etc - can be shown to be equal to interpolating prior to draws
    #should have already interpolated i3950 and i4250 correctly, just need to do the other two indices
#DOUBLE CHECK THE ACTUAL NARROW BAND ENDPOINTS USED HERE...
    low_w_n_3850=low_w_n[0]
    high_w_n_4100=high_w_n[-1]
    errcheck_n=0
    for entry in range(len(low_w)):
        if low_w[entry]==low_w_n_3850:
            low_f_n[0]=(low_f[entry]-low_f[entry-1])/(low_w[entry]-low_w[entry-1])*(i3850-low_w[entry-1])+low_f[entry-1]
            errcheck_n+=1
    for entry in range(len(high_w)):
        if high_w[entry]==high_w_n_4100:
            high_f_n[-1]=(high_f[entry+1]-high_f[entry])/(high_w[entry+1]-high_w[entry])*(i4100-high_w[entry+1])+high_f[entry+1]
            errcheck_n+=1
    if int(errcheck_n)!=2:
        print('error in d4k_n interpolation, errcheck_n value='+str(errcheck_n))
    return{'low_f':low_f,'high_f':high_f,'low_f_n':low_f_n,'high_f_n':high_f_n,'error':'none'}

def D_4k(low_f,high_f): #measures d4k
    d4000=np.mean(high_f)/np.mean(low_f)
    return{'d4000':d4000}
    
def D_4k_n(low_f_n, high_f_n): #measures d4kn
    d4000=np.mean(high_f_n)/np.mean(low_f_n)    
    return{'d4000_n':d4000}
    
def per_gal_d4k(filename, zfilename): #calls previous functions, etc. to return d4k + unc for a single galaxy, and flags
    seed=zfilename.split('_')[2]
    seed=int(seed.split('.')[0])
    rn.seed(int(time.time())+seed)
    errflags=''    
    parse=specpars(filename,zfilename)
    if parse['iserror']:
        errflags+='Y'
    else:
        errflags+='n'
    flag=False #Flag to indicate whether or not to draw for d4k or use measured values
    flag2=True #flag to tell rshift draw to interpolate to smooth redshift prob grid
    keepgoing=True #flag to indicate whether or not to proceed with MC. False if cannot get measured d4k
    iterations=100001 #monte carlo iterations +1 for measured loop (3000 after noting 1000 not stable always)
    boundscounter=0
    nancounter=0
    temp4k = []
    temp4kn = []
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
            fluxes=flux_draw(parse['wavelength'],parse['flux'],parse['error'],reds['i39'],reds['i37'],reds['i42'],reds['i40'],reds['i38'],reds['i41'],reds['n40'],flag)
            if fluxes['error']!='none': #some error flag work
                if fluxes['error']=='outofbounds':
                    d4k='-99'
                    d4kn='-99'
                    unc_d4k_high='-99'
                    unc_d4k_low='-99'
                    unc_d4kn_high='-99'
                    unc_d4kn_low='-99'
                    grism_z=reds['grizm']
                    errflags+='1-'
                    keepgoing=False
                elif fluxes['error']=='nancheck':
                    d4k='-99'
                    d4kn='-99'
                    unc_d4k_high='-99'
                    unc_d4k_low='-99'
                    unc_d4kn_high='-99'
                    unc_d4kn_low='-99'
                    grism_z=reds['grizm']
                    errflags+='2-'
                    keepgoing=False
            else: #measures d4k if everything okay
                wide=D_4k(fluxes['low_f'],fluxes['high_f'])
                narrow=D_4k_n(fluxes['low_f_n'],fluxes['high_f_n'])
                d4k=wide['d4000']
                d4kn=narrow['d4000_n']
                grism_z=reds['grizm']
                errflags+='n'
        elif keepgoing and flag: #monte carlo work
            reds=rshift_draw(parse['redshifts'],parse['o_probabilities'],flag,smoothprob,smoothred,flag2)
            redshiftlist.append(reds['grizm'])
            smoothprob=reds['smp']
            smoothred=reds['smr']
            flag2=False
            fluxes=flux_draw(parse['wavelength'],parse['flux'],parse['error'],reds['i39'],reds['i37'],reds['i42'],reds['i40'],reds['i38'],reds['i41'],reds['n40'],flag)
            if fluxes['error']!='none': #error flags for MC
                if fluxes['error']=='outofbounds':
                    boundscounter+=1
                elif fluxes['error']=='nancheck':
                    nancounter+=1
            else: #calculates MC d4k
                wide=D_4k(fluxes['low_f'],fluxes['high_f'])
                narrow=D_4k_n(fluxes['low_f_n'],fluxes['high_f_n'])
                temp4k.append(wide['d4000'])
                temp4kn.append(narrow['d4000_n'])
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
        temp4k=sorted(temp4k)
        temp4kn=sorted(temp4kn)
        w68=[]
        n68=[]
        t4k_h,t4k_l,t4kn_h,t4kn_l=([] for i in range(4))
        for entry in range(len(temp4k)):
            temp4k[entry]=temp4k[entry]-d4k
            if temp4k[entry]>0.0:
                t4k_h.append(temp4k[entry])
            else:
                t4k_l.append(temp4k[entry])
        for entry in range(len(temp4kn)):
            temp4kn[entry]=temp4kn[entry]-d4kn
            if temp4kn[entry]>0.0:
                t4kn_h.append(temp4kn[entry])
            else:
                t4kn_l.append(temp4kn[entry])
        for entry in range(len(t4k_l)):
            if float(entry+1)/float(len(t4k_l))>0.32:
                w68.append(t4k_l[entry])
        for entry in range(len(t4k_h)):
            if float(entry+1)/float(len(t4k_h))<0.68:
                w68.append(t4k_h[entry])
        for entry in range(len(t4kn_l)):
            if float(entry+1)/float(len(t4kn_l))>0.32:
                n68.append(t4kn_l[entry])
        for entry in range(len(t4kn_h)):
            if float(entry+1)/float(len(t4kn_h))<0.68:
                n68.append(t4kn_h[entry])
        unc_d4k_high=w68[-1]
        unc_d4k_low=w68[0]
        unc_d4kn_high=n68[-1]
        unc_d4kn_low=n68[0]
        if boundscounter>=0.1*(iterations-1) and boundscounter<0.3*(iterations-1):
            errflags+='1'
        elif boundscounter>=0.3*(iterations-1):
            errflags+='2'
        elif nancounter>=0.1*(iterations-1) and nancounter<0.3*(iterations-1):
            errflags+='3'
        elif nancounter>=0.3*(iterations-1):
            errflags+='4'
        else:
            errflags+='n'
    return([d4k,unc_d4k_high,unc_d4k_low,d4kn,unc_d4kn_high,unc_d4kn_low,errflags,grism_z,unc_red_high,unc_red_low,unc_redhigh95,unc_redlow95,unc_redhigh99,unc_redlow99])

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
    #processcount=1s
    results=multicore(filename,zfilename,processcount)
    filewrite=open(outputname,'w')
    filewrite.write('D4000.py version 06.09.15\n') #UPDATE VERSION AFTER CHANGES
    filewrite.write('FLAG KEY: \n')
    filewrite.write('nnnn:\tnormal\nYnnn:\tmismatch between lengths of flux, wave, error, etc\nnYnn:\terror drawing redshift, 0.0 used instead\nnn1n:\tout of bounds on measured d4k\nnn2n:\tnans in measured d4k\nnnn1,2:\t>10%,50% out of bounds for MC\nnnn3,4:\t>10%,50% nans for MC\n')
    filewrite.write('\nname'+'\t'+'d4k'+'\t'+'unc_d4k_high'+'\t'+'unc_d4k_low'+'\t'+'d4kn'+'\t'+'unc_d4kn_high'+'\t'+'unc_d4kn_low'+'\t'+'grism_z'+'\t'+'unc_redhigh68'+'\t'+'unc_redlow68'+'\t'+'unc_redhigh95'+'\t'+'unc_redlow95'+'\t'+'unc_redhigh99'+'\t'+'unc_redlow99'+'\t'+'flag'+'\n')
    for key,entry in results.items():
        filewrite.write(str(key)+'\t'+str(entry[0])+'\t'+str(entry[1])+'\t'+str(entry[2])+'\t'+str(entry[3])+'\t'+str(entry[4])+'\t'+str(entry[5])+'\t'+str(entry[7])+'\t'+str(entry[8])+'\t'+str(entry[9])+'\t'+str(entry[10])+'\t'+str(entry[11])+'\t'+str(entry[12])+'\t'+str(entry[13])+'\t'+str(entry[6])+'\n')
    filewrite.close()
    elapsed_time = time.time() - start_time
    print("Executed in "+str(elapsed_time)+"s")
    
###############################################################################
###########################______PROGRAM______#################################
###############################################################################
Wrapper()