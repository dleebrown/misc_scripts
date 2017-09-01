# reads in aspcapstar fits file, and the aspcapstar wavelength grid, and exports the results to text file

import numpy as np
from astropy.io import fits

image_name = '7417074'
data_or_model = 'data'

path_to_data = '/home/donald/Desktop/grayson_spectra/'
wavegrid = np.loadtxt(path_to_data+'apstar_wavegrid')

fits_image = fits.open(path_to_data+image_name+'.fits')

output_array = np.zeros((np.size(wavegrid), 2))

if data_or_model == 'data':
    fluxdata = fits_image[1].data
    output_array[:, 0] = wavegrid
    output_array[:, 1] = fluxdata
    np.savetxt(path_to_data+image_name+'_data', output_array)
else:
    fluxdata = fits_image[3].data
    output_array[:, 0] = wavegrid
    output_array[:, 1] = fluxdata
    np.savetxt(path_to_data+image_name+'_model', output_array)

