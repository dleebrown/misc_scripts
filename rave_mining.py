import pandas as pd

#read in full catalog
catalog=pd.DataFrame(pd.read_csv('C:\Users\Donald\Desktop\RAVE_DR4.csv', low_memory=False))

#store column names and data types in lists
colnames=list(catalog.columns.values)
datatypes=list(catalog.dtypes)

#remove non float entries from the metallicity column, convert column to float
catalog=catalog[catalog.Met_N_K.str.contains('\N')==False]
catalog['Met_N_K']=catalog['Met_N_K'].astype(float)

#turn metallicity algorithm convergence column to int, select only convergent metallicity solutions
catalog['Algo_Conv_K']=catalog['Algo_Conv_K'].astype(int)
colnames=list(catalog.columns.values)
catalog=catalog[catalog['Algo_Conv_K']==0]

#select only stars with declinations above -15:
catalog=catalog[catalog['DEdeg']>-15]

#select only stars with metallicities above 0.3
catalog=catalog[catalog['Met_N_K']>0.3]

#select only stars with effective temps >5800 and <6500
catalog['Teff_K']=catalog['Teff_K'].astype(float)
catalog=catalog[catalog['Teff_K']>5800]
catalog=catalog[catalog['Teff_K']<6500]

#select only stars with gravities > 3.0
catalog['logg_K']=catalog['logg_K'].astype(float)
catalog=catalog[catalog['logg_K']>3.0]

catalog.to_csv(r'C:\Users\Donald\Desktop\RAVE_mined.csv')