__author__ = 'donald'
    #essentially a translation of http://idlastro.gsfc.nasa.gov/ftp/pro/astro/calz_unred.pro to python:
"""
; NAME:
;     CALZ_UNRED
; PURPOSE:
;     Deredden a galaxy spectrum using the Calzetti et al. (2000) recipe
; EXPLANATION:
;     Calzetti et al.  (2000, ApJ 533, 682) developed a recipe for dereddening
;     the spectra of galaxies where massive stars dominate the radiation output,
;     valid between 0.12 to 2.2 microns.     (CALZ_UNRED extrapolates between
;     0.12 and 0.0912 microns.)
;
; CALLING SEQUENCE:
;     CALZ_UNRED, wave, flux, ebv, [ funred, R_V = ]
; INPUT:
;      WAVE - wavelength vector (Angstroms)
;      FLUX - calibrated flux vector, same number of elements as WAVE
;               If only 3 parameters are supplied, then this vector will
;               updated on output to contain the dereddened flux.
;      EBV  - color excess E(B-V), scalar.  If a negative EBV is supplied,
;               then fluxes will be reddened rather than deredenned.
;               Note that the supplied color excess should be that derived for
;               the stellar  continuum, EBV(stars), which is related to the
;               reddening derived from the gas, EBV(gas), via the Balmer
;               decrement by EBV(stars) = 0.44*EBV(gas)
;
; OUTPUT:
;      FUNRED - unreddened flux vector, same units and number of elements
;               as FLUX.   FUNRED values will be zeroed outside valid domain
;               Calz_unred (0.0912 - 2.2 microns).
;
; OPTIONAL INPUT KEYWORD:
;       R_V - Ratio of total to selective extinction, default = 4.05.
;             Calzetti et al. (2000) estimate R_V = 4.05 +/- 0.80 from optical
;             -IR observations of 4 starbursts.
; EXAMPLE:
;       Estimate how a flat galaxy spectrum (in wavelength) between 1200 A
;       and 3200 A is altered by a reddening of E(B-V) = 0.1.
;
;       IDL> w = 1200 + findgen(40)*50      ;Create a wavelength vector
;       IDL> f = w*0 + 1                    ;Create a "flat" flux vector
;       IDL> calz_unred, w, f, -0.1, fnew  ;Redden (negative E(B-V)) flux vector
;       IDL> plot,w,fnew
"""

import numpy as np
#wavelength in angstroms, flux in flux, ebv is a scalar. if ebv is negative, the script will redden the flux
#r_v is hardcoded to be 4.05 for calzetti
def calzetti_deredden(wavelength,flux,ebv):
    r_v=4.05
    w1=np.where(abs(wavelength-14150)<=7850)
    w2=np.where(abs(wavelength-3606)<=2694)
    x=10000.0/wavelength
    klam=0.0*flux
    if np.size(w1)+np.size(w2)!=len(wavelength):
        print("warning, some elements of wavelength vector outside valid domain")
    if len(w1)>0:
        klam[w1]=2.659*(-1.857+1.040*x[w1])+r_v
    if len(w2)>0:
        klam[w2]=2.659*(-2.156+1.509*x[w2]-0.198*x[w2]**2+0.011*x[w2]**3)+r_v
    funred=flux*10.0**(0.4*klam*ebv)
    return(funred)

ebv=-1/4.05
#give the central wavelengths for UVJ based on 3dhst header, in A
wavelengths=np.array([3598.5,5490.6,12375.1]) #these are for 3dhst U,V,J
flux=np.array([1.0,1.0,1.0])
reddened=calzetti_deredden(wavelengths,flux,ebv)

#print reddened flux
print reddened

#compute U-V, V-J shifts, assuming flux = 1 to begin with
UV=-2.5*np.log10(reddened[0]/reddened[1])
VJ=-2.5*np.log10(reddened[1]/reddened[2])

print UV, VJ