import readmultispec as rmspec
from scipy import interpolate as ip
import numpy as np
from matplotlib import pyplot as plt

# reads in a multispec file and parses it, returns 2D array with wavelength, flux for given line
def read_multispec_file(image, line):
    image = rmspec.readmultispec(image)
    wavelengths = image['wavelen']
    flux = image['flux']
    # for now just make ids a np arange until I figure out how to hook the WOCS IDs
    num_waves = len(wavelengths[line])
    output_array = np.zeros((num_waves, 2), dtype=np.float32)
    output_array[:, 0] = wavelengths[line]
    output_array[:, 1] = flux[line]
    return output_array

def just_plot(spectrum1, spectrum2, label1, label2):
    #interpolates spectrum 1 onto spectrum 2 grid, plots with labels
    mmin=500
    mmax=1000
    fig, splot = plt.subplots()
    splot.plot(spectrum2[:, 0], spectrum2[:, 1], color='FireBrick', linewidth=2.5,
               label=label2)
    splot.plot(spectrum1[:, 0], spectrum1[:, 1], color='RoyalBlue', linewidth=2.5,
               label=label1)
    splot.legend(loc=4)
    plt.savefig(label1+'_'+label2+'_uninterp_overplot', format='pdf', bbox_inches='tight')
    plt.show()

def interp_and_plot(spectrum1, spectrum2, label1, label2):
    #interpolates spectrum 1 onto spectrum 2 grid, plots with labels
    mmin=500
    mmax=1000
    interp_wave_grid = spectrum2[:, 0]
    function = ip.interp1d(spectrum1[:, 0], spectrum1[:, 1], kind='linear', bounds_error=False, fill_value=1.0)
    interpolated_spectrum = function(interp_wave_grid)
    fig, splot = plt.subplots()
    splot.plot(spectrum2[mmin:mmax, 0], spectrum2[mmin:mmax, 1], color='FireBrick', linewidth=2.5,
               label=label2)
    splot.plot(spectrum2[mmin:mmax, 0], interpolated_spectrum[mmin:mmax], color='RoyalBlue', linewidth=2.5,
               label=label1)
    splot.legend(loc=4)
    plt.savefig(label1+'_'+label2+'_overplot', format='pdf', bbox_inches='tight')
    plt.show()

def divide_and_plot(spectrum1, spectrum2, label1, label2):
    #interpolates spectrum 1 onto spectrum 2 grid, plots with labels
    mmin=500
    mmax=1000
    interp_wave_grid = spectrum2[:, 0]
    function = ip.interp1d(spectrum1[:, 0], spectrum1[:, 1], kind='linear', bounds_error=False, fill_value=1.0)
    interpolated_spectrum = function(interp_wave_grid)
    fig, splot = plt.subplots()
    splot.plot(spectrum2[mmin:mmax, 0], spectrum2[mmin:mmax, 1]/interpolated_spectrum[mmin:mmax], color='FireBrick', linewidth=2.5,
               label=label2+'/'+label1)
    splot.legend(loc=4)
    plt.savefig(label1+'_'+label2+'_div', format='pdf', bbox_inches='tight')
    plt.show()

first_file = '6819E.fits'
first_fitsline = 40
first_label = '6819E-45020'

second_file = '6819D.fits'
second_fitsline = 43
second_label = '6819D-33012'

"""
first = read_multispec_file(first_file, first_fitsline)
second = read_multispec_file(second_file, second_fitsline)

just_plot(first, second, first_label, second_label)
interp_and_plot(first, second, first_label, second_label)
divide_and_plot(first, second, first_label, second_label)
"""

test_file = '2506_robosample.fits'
test_line = np.arange(0,78,1)
for i in test_line:
    first = read_multispec_file(test_file, test_line[i])
