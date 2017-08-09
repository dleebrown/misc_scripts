import numpy as np
import random

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

input_spec = np.genfromtxt('0.001.vsn.spec')
sn_profile = np.genfromtxt('sn.robo.template')

output_fluxes = sn_adder(input_spec[:, 0], input_spec[:, 1], sn_profile, 225.0)
input_spec[:, 1] = output_fluxes[:]

np.savetxt('0.001.noised.spec', input_spec)