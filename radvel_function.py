import random
from scipy import interpolate as ip


def radVel(wavelengths, fluxes, rv_range):
    """Adds radial velocity shift to a star based on a tuple of ranges (in km/s)
    Does this by shifting the wavelength grid and remapping the original flux values to that shifted grid,
    Then interpolating those flux values back into the original wavelength grid. 
    Flux values outside the interpolation range are set to 1.0. wavelengths and fluxes should be 1D numpy arrays
    rv_range should be a tuple of floats. Returns a 1D numpy array of length(wavelengths)"""
    radvel = random.uniform(float(rv_range[0]), float(rv_range[1]))  # draw the radvel
    shifted_wave = wavelengths + (radvel*wavelengths)/3.0e5  # calculate the shifted wavelength grid
    shifted_flux = ip.interp1d(shifted_wave, fluxes, kind='linear', bounds_error=False, fill_value=1.0)  # define interp
    output_fluxes = shifted_flux(wavelengths)  # interpolate shifted spectrum onto initial wavelength grid
    return output_fluxes

