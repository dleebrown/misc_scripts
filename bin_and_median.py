"""takes in a 2 column comma-delimited csv file that has columns: true_param, inferred_param (with no header).
Bins by true param and calculates median inferred param in each bin. Then saves these as a text file to eventually be 
fit somewhere else. output file has columns median_true, median_inferred"""

import numpy as np

#files should have the form param_name+data.csv. so for example below, the file would be rotdata.csv. 
parameter_name = 'rot'

# control the number of bins. This actually slices into bins of equal numbers of examples, rather than by equal ranges
# in parameter (i.e. 100 examples per bin, rather than all examples between Teff=5000 and 6000.
# But this shouldn't matter for the sample sizes we're working with.
num_bins = 20

#load the data and sort it by true parameter. 
param_data = np.loadtxt(parameter_name+'data.csv', delimiter=',')
param_data = np.sort(param_data, axis=0)

#slice out true and inferred data. 
true_data = param_data[:, 0]
infer_data = param_data[:, 1]

slice_size = int(np.size(true_data)/num_bins)

# actually calculate the medians. 
output_stats = np.zeros((num_bins, 2))
for i in range(num_bins):
    output_stats[i, 0] = np.median(true_data[i*slice_size:slice_size*(i+1)])
    output_stats[i, 1] = np.median(infer_data[i*slice_size:slice_size*(i+1)])

# saves the results in a file, e.g., 'rotmedian.out' where the first column is median true stat,
# second is median inferred stat.
np.savetxt(parameter_name+'.median.out', output_stats)
