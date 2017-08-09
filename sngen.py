"""
v1.0: Takes in input spectra (presumably real, so that they have the instrumental response baked in) and outputs
an estimate of the per-pixel SN, relative to a specified wavelength region. E.g., specify the region 6785-6795 A as
the benchmark region. The code will then take in the input files, measure the SN in that region in all of them, then
output the per-pixel SN across the entire set of input spectra _relative_ to the specified region, which is then set to
"1.0" SN.

Input: bunch of spectra with same wavelength range and spacing ('*.spec'), benchmark region
Output: file with 2 columns: wavelength, per-pixel relative SN to input region ('sn.template')

This is more like a script than proper code so it's pretty brittle

After testing, this really needs to be run on either a) featureless spectra (hot stars) or b) line extracted spectra
"""

import numpy as np
import math
import glob


def readin(filelist):
    """Reads in and parses files, returns numpy array with columns wavelength, star1 flux, star2 flux..."""
    example_file = np.genfromtxt(filelist[0])  # opens first file to get number of pixels, wavelengths
    wavelengths = example_file[:, 0]
    num_pixels = np.size(wavelengths)
    output = np.zeros((num_pixels, len(filelist)+1))  # creates output file
    output[:, 0] = wavelengths
    for i in range(1, len(filelist)+1):
        temp_data = np.genfromtxt(filelist[i-1])  # reads in each file and puts fluxes into output array
        output[:, i] = temp_data[:, 1]
    return output


def measure_sn(input_array, window):
    """takes in an array with columns, wavelength, star1 flux..., and window width (in pixels for now)
    calculates the SN in a window around each pixel (at endpoints, uses half-window)
    The method for calculating SN is as follows: in each window, calculates median pixel value,
    then calculates the MAD about the median, and arrives at the noise by N = 1.48 * MAD. Then flux/noise = SN
    """
    npx, nst = np.shape(input_array)
    sn_array = np.zeros(np.shape(input_array))
    sn_array[:, 0] = input_array[:, 0]
    for star in range(1, nst):  # loops over both stars and pixels
        for px in range(npx):
            # truncate to lowest/highest possible pixel for median calculation
            lower_index = max([px-int(math.ceil(window/2)), 0])
            upper_index = min([px+int(math.ceil(window/2)), npx-1])
            # calculate the MAD
            temp_mad = input_array[lower_index: upper_index, star]
            median = np.median(temp_mad)
            temp_mad = np.absolute(temp_mad-median)
            # calculate SN and put into output array
            sn_array[px, star] = input_array[px, star]/(1.48*np.median(temp_mad))
    return sn_array


def relative_mean_sn(sn_array, lower_wave, upper_wave):
    """Takes in an array with columns, wavelength, star1 SN..., and upper and lower bounds (in A) for
    the baseline SN calculation. Returns an array with 2 columns, wavelength, relative SN,
    where the relative SN is relative to the mean SN in the range [lower_wave, upper_wave], which is set to 1"""
    npx, nst = np.shape(sn_array)
    mean_sn = np.zeros((npx, 2))  # create array to put mean SN values in for each wavelength
    mean_sn[:, 0] = sn_array[:, 0]  # add wavelengths
    only_sn = sn_array[:, 1:]  # trim sn_array to remove wavelength column
    baseline_sn = np.mean(only_sn[(lower_wave <= mean_sn[:, 0]) & (mean_sn[:, 0] <= upper_wave)], 0)  # base SN
    only_sn = only_sn / baseline_sn # calculate per pixel relative SN
    mean_sn[:, 1] = np.mean(only_sn, axis=1)  # calculate per pixel mean relative SN
    mean_sn[(lower_wave <= mean_sn[:, 0]) & (mean_sn[:, 0] <= upper_wave), 1] = 1.0  # set base SN range = 1.0
    return mean_sn


def read_files(suffix='*.spec'):
    """constructs list of files with given suffix, returns list with filenames"""
    filelist = glob.glob(suffix)
    return filelist


def write_file(mean_file, name='sn.template'):
    np.savetxt(name, mean_file)
    print('relative mean SN written to '+name)


if __name__ == "__main__":
    # variables used
    boxcar = 30
    lwave = 6789.0
    uwave = 6791.0
    # program
    files = read_files()
    flux_array = readin(files)
    snr_array = measure_sn(flux_array, boxcar)
    mean_sn = relative_mean_sn(snr_array, lwave, uwave)
    write_file(mean_sn)
