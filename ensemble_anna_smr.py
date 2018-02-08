"""
computes the weighted statistics for the 6 different ANNA runs for the SMR sample
the concatenated outputs as well as the solar benchmark should be in the same folder per model
"""

import numpy as np
import collections

# define the various directories and standardized file names
parent_dir = '/home/donald/current_work/MY_THESIS/'
run1 = 'thesis_anna_infer_r1/'
run2 = 'thesis_anna_infer_r2/'
run3 = 'these_anna_infer_r3/'
run4 = 'these_anna_infer_r4/'
run5 = 'thesis_anna_infer_r5/'
run6 = 'thesis_anna_infer_r6/'

smr_outfile = 'concatenated_outputs'
solar_outfile = 'jun2011_3133.fits_infer.out'

run_dirs = collections.OrderedDict()
run_dirs['r1'] = parent_dir+run1
run_dirs['r2'] = parent_dir+run2
run_dirs['r3'] = parent_dir+run3
run_dirs['r4'] = parent_dir+run4
run_dirs['r5'] = parent_dir+run5
run_dirs['r6'] = parent_dir+run6


def import_run_results(directory):
    smr_results = np.genfromtxt(directory+smr_outfile, delimiter=' ', skip_header=0)
    smr_temps = smr_results[:, 1]
    smr_metals = smr_results[:, 3]
    solar_results = np.genfromtxt(directory+solar_outfile, delimiter=',', skip_header=1)
    solar_temps = solar_results[:, 1]
    solar_metals = solar_results[:, 3]
    return smr_temps, smr_metals, solar_temps, solar_metals


# snag the relevant information
smrt, _, solt, _ = import_run_results(run_dirs['r1'])

all_smr_temps = np.zeros((np.size(smrt), 6))
all_smr_metals = np.zeros((np.size(smrt), 6))

all_solar_temps = np.zeros((np.size(solt), 6))
all_solar_metals = np.zeros((np.size(solt), 6))

counter = 0
for run in run_dirs:
    smt, smm, sot, som = import_run_results(run_dirs[run])
    all_smr_temps[:, counter] = smt
    all_smr_metals[:, counter] = smm
    all_solar_temps[:, counter] = sot
    all_solar_metals[:, counter] = som
    counter += 1

# now make an array with solar statistics
solar_temp_stats = np.zeros((2, 6))
solar_metal_stats = np.zeros((2, 6))

for i in range(6):
    solar_temp_stats[0, i] = np.mean(all_solar_temps[:, i])
    solar_temp_stats[1, i] = np.std(all_solar_temps[:, i])
    solar_metal_stats[0, i] = np.mean(all_solar_metals[:, i])
    solar_metal_stats[1, i] = np.std(all_solar_metals[:, i])

canonical_solar_temp = 5770.0
canonical_solar_metal = 0.00

# now build an array that contains the norm weights (determined by 1/|dev_from_canonical|) - temp and metal in diff rows
weight_values = np.zeros((2, 6))
for i in range(6):
    weight_values[0, i] = 1/np.abs((solar_temp_stats[0, i]-5770.0))
    weight_values[1, i] = 1/np.abs(solar_metal_stats[0, i])

weight_values[0, :] = weight_values[0, :]/np.sum(weight_values[0, :])
weight_values[1, :] = weight_values[1, :]/np.sum(weight_values[1, :])

# now as a check compute the weighted solar temperature and metallicity with stat uncertainties
weighted_solar_temps = []
weight_solar_temp_std = []
weighted_solar_metals = []
weight_solar_metal_std = []

for i in range(6):
    weighted_solar_temps.append(solar_temp_stats[0, i]*weight_values[0, i])
    weight_solar_temp_std.append(solar_temp_stats[1, i]*weight_values[0, i])
    weighted_solar_metals.append(solar_metal_stats[0, i]*weight_values[1, i])
    weight_solar_metal_std.append(solar_metal_stats[1, i]*weight_values[1, i])

weight_stemp = np.sum(weighted_solar_temps)
weight_stemp_std = np.sum(weight_solar_temp_std)
weight_smet = np.sum(weighted_solar_metals)
weight_smet_std = np.sum(weight_solar_metal_std)

print(weight_stemp, weight_smet)
print(weight_stemp_std, weight_smet_std)

# okay that all looks very nice now apply the weights to the smr stars and compute the weighted stdev too

weighted_smr_temps = np.zeros((np.size(all_smr_temps[:, 0]), 2))
weighted_smr_metals = np.zeros((np.size(all_smr_metals[:, 0]), 2))

temp_weight_array = np.copy(all_smr_temps[:, :])
metal_weight_array = np.copy(all_smr_metals[:, :])

for i in range(6):
    temp_weight_array[:, i] = temp_weight_array[:, i]*weight_values[0, i]
    metal_weight_array[:, i] = metal_weight_array[:, i]*weight_values[1, i]

weighted_smr_temps[:, 0] = np.sum(temp_weight_array, axis=1)
weighted_smr_metals[:, 0] = np.sum(metal_weight_array, axis=1)


# now compute the weighted standard deviation for each star parameters

temp_deviations_array = np.copy(all_smr_temps[:, :])
metal_deviations_array = np.copy(all_smr_metals[:, :])

weighted_sum_array_temp = np.zeros((np.size(all_smr_temps[:, 0]), 1))
weighted_sum_array_met = np.zeros((np.size(all_smr_temps[:, 0]), 1))

for i in range(6):
    temp_deviations_array[:, i] = weight_values[0, i]*(temp_deviations_array[:, i] - weighted_smr_temps[:, 0])**2
    metal_deviations_array[:, i] = weight_values[1, i]*(metal_deviations_array[:, i] - weighted_smr_metals[:, 0])**2

weighted_sum_array_temp[:, 0] = np.sqrt(np.sum(temp_deviations_array, axis=1)/(5.0/6.0))
weighted_sum_array_met[:, 0] = np.sqrt(np.sum(metal_deviations_array, axis=1)/(5.0/6.0))

# okay so there's those. now combine those in quadrature with the weighted statistical errors derived from the sun
weighted_sum_array_temp = np.sqrt(weighted_sum_array_temp**2 + weight_stemp_std**2)
weighted_sum_array_met = np.sqrt(weighted_sum_array_met**2 + weight_smet_std**2)

weighted_smr_temps[:, 1] = weighted_sum_array_temp[:, 0]
weighted_smr_metals[:, 1] = weighted_sum_array_met[:, 0]

# so now we have everything we need I believe. concatenate the two arrays and save the results to disk

save_loc = '/home/donald/current_work/MY_THESIS/'
save_name = 'weighted_temp_met_SMR'

output_array = np.concatenate((weighted_smr_temps, weighted_smr_metals), axis=1)

np.savetxt(save_loc+save_name, output_array)



















