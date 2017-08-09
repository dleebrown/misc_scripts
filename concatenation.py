import pandas as pd

#read in all catalogs, which have already been trimmed for correct Teff, metallicities, logg, and coordinates (where the params exist)
gc=pd.DataFrame(pd.read_csv(r'C:\Users\Donald\Desktop\GC_match.csv', low_memory=False))
pastel=pd.DataFrame(pd.read_csv(r'C:\Users\Donald\Desktop\pastel_match.csv', low_memory=False))
n2k=pd.DataFrame(pd.read_csv(r'C:\Users\Donald\Desktop\n2k_match.csv', low_memory=False))
hypatia=pd.DataFrame(pd.read_csv(r'C:\Users\Donald\Desktop\hypatia_match.csv', low_memory=False))
rave=pd.DataFrame(pd.read_csv(r'C:\Users\Donald\Desktop\rave_match.csv', low_memory=False))
progress=pd.DataFrame(pd.read_csv(r'C:\Users\Donald\Desktop\progress_match.csv', low_memory=False))

catalog=pd.merge(gc,n2k,how='outer',on='MAIN_ID')
catalog=pd.merge(catalog,pastel,how='outer',on='MAIN_ID')
catalog=pd.merge(catalog,hypatia,how='outer',on='MAIN_ID')
catalog=pd.merge(catalog,rave,how='outer',on='MAIN_ID')
catalog=pd.merge(catalog,progress,how='outer',on='MAIN_ID')


#catalog.T.drop_duplicates().T

catalog.to_csv(r'C:\Users\Donald\Desktop\SMR_catalog_full.csv')
