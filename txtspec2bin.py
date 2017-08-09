from scipy import interpolate as ip
import numpy as np
import glob
from array import array
import subprocess


def binaryPack(input_file, output_file, atm_parameters, first='yes'):
    input_spec = np.genfromtxt(input_file)
    if first == 'yes':
        wavelength = input_spec[:, 0]
        # dumps #px, #params, wavelengths to beginning of file
        pwavelength = np.zeros(len(wavelength) + 2)
        pwavelength[0] = float(len(wavelength))
        pwavelength[1] = float(len(atm_parameters)-2)
        pwavelength[2:] = wavelength
        w_array = array('d', pwavelength)
        # now params, fluxes for first star
        a_array = array('d', atm_parameters)
        flux = input_spec[:, 1]
        f_array = array('d', flux)
        w_array.tofile(output_file)
        a_array.tofile(output_file)
        f_array.tofile(output_file)
        # subprocess.call(['rm', input_file])
    else:
        # now just dumps params, fluxes for stars 2 to N
        flux = input_spec[:, 1]
        f_array = array('d', flux)
        a_array = array('d', atm_parameters)
        a_array.tofile(output_file)
        f_array.tofile(output_file)
        # subprocess.call(['rm', input_file])

if __name__ == "__main__":

    binary_out = 'YES'
    verbose = 'YES'

    fitsrows = [2, 3, 5, 6, 8, 10, 11, 12, 13, 14, 30, 31, 32, 33, 34, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 53,
                54, 55, 61]
    wavegrid = str('wavelength.template')
    gridme = np.loadtxt(wavegrid)[:, 0]
    for entry in fitsrows:
        interpolateme = np.loadtxt(str(entry)+'.vsn.spec')
        inputfile = str(entry)+'.vsn.spec'
        function = ip.interp1d(interpolateme[:, 0], interpolateme[:, 1], kind='linear')
        interpolated = function(gridme)
        outputarray = np.zeros((len(gridme), 2))
        outputarray[:, 0] = gridme
        outputarray[:, 1] = interpolated
        np.savetxt(inputfile+'.i', outputarray)

    if binary_out == 'YES':
        print('binary output construction')
        # open binary file
        binary_output = open('solar_test', 'wb')
        # get list of postprocessed files
        atmparams = np.genfromtxt('atmparams.solar.out', delimiter=',', skip_header=1)
        # write everything to binary file
        for i in range(len(atmparams[:, 0])):
            starname = str(int(atmparams[i, 0]))
            if i == 0:
                binaryPack(starname + '.vsn.spec.i', binary_output, atmparams[i, :], first='yes')
            else:
                binaryPack(starname + '.vsn.spec.i', binary_output, atmparams[i, :], first='no')
        binary_output.close()
        # remove *.vsn.spec files if specified (by default this is on)
        if verbose == 'NO':
            filelist = glob.glob('*.vsn.spec.i')
            print('binary output only; removing individual postprocessed spectra')
            for fl in filelist:
                subprocess.call(['rm', fl])
