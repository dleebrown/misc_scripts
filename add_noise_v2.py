import numpy as np
import random
import os

# adds SN profile to all .spec files in a directory according to the snvalue specified below and the default
# sn template name I use
snvalue = 200.0

def grab_specnames(path='./'):
    allfiles = os.listdir(path)
    specfiles = []
    for i in allfiles:
        if '.spec' in i:
            specfiles.append(i)
    return specfiles


def sn_adder(wavelengths, fluxes, relative_sn, sn):
    """Takes in 2d array with columns wavelength, flux
    and 2d array with columns wavelength, relative sn
    interpolates the relative sn array onto the spectrum wavelengths
    then noises (gaussian) the spectrum according to the sn_array
    with some sn drawn from sn_range (2 entry iterable)
    also randomly shifts the median flux of the spectrum by a set amount across the spectrum.
    """
    interp_sn = np.interp(wavelengths, relative_sn[:, 0], relative_sn[:, 1])
    base_std = 1.0 / float(sn)
    noise_array = np.random.normal(0.0, scale=base_std, size=(len(wavelengths)))
    fluxes += noise_array*interp_sn
    fluxes += random.uniform(-0.010, 0.010)
    return fluxes

def add_sn_to_all(filelist, snfile, sn_to_add):
    sn_profile = np.genfromtxt(snfile)
    for i in filelist:
        input_spec = np.genfromtxt(i)
        output_fluxes = sn_adder(input_spec[:, 0], input_spec[:, 1], sn_profile, sn_to_add)
        input_spec[:, 1] = output_fluxes[:]
        np.savetxt(i+'.sn', input_spec)

files_to_sn = grab_specnames()
add_sn_to_all(files_to_sn, 'sn.robo.template', snvalue)

