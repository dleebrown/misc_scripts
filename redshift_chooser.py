__author__ = 'donald'
#takes in csv containing 7 columns titled as follows:
#galaxy_id, g102_z,g102_uh,g102_ul,g141_z,g141_uh,g141_ul
#where the uncertainties correspond to some confidence interval (assumed 68%)
#then compares the redshifts for each galaxy:
#if either redshift is within the 68% interval of the other, initiates a test
#and selects the best-constrained redshift between g102 and g141
#HDif the two distributions are mutually exclusive, returns a flag for that galaxy
#outputs a file with galaxy id, redshift+unc, and source of redshift (g102 or g141)
import pandas as pd

def Comparator(galaxy_z): #compares redshifts, returns True if test passed
    g102_high=galaxy_z[1]+galaxy_z[2]
    g102_low=galaxy_z[1]-galaxy_z[3]
    g141_high=galaxy_z[4]+galaxy_z[5]
    g141_low=galaxy_z[4]-galaxy_z[6]
    if galaxy_z[4]<=g102_high and galaxy_z[4]>=g102_low:
        return(True)
    elif galaxy_z[1]<=g141_high and galaxy_z[1]>=g141_low:
        return(True)
    else:
        return(False)

def Tester(galaxy_z): #tests and returns the best redshift,unc,and grism choice
    g102_high=galaxy_z[1]+galaxy_z[2]
    g102_low=galaxy_z[1]-galaxy_z[3]
    g141_high=galaxy_z[4]+galaxy_z[5]
    g141_low=galaxy_z[4]-galaxy_z[6]
    g102_range=abs(g102_high-g102_low)
    g141_range=abs(g141_low-g141_high)
    if g102_range<=g141_range:
        return([galaxy_z[0],galaxy_z[1],galaxy_z[2],galaxy_z[3],'g102'])
    else:
         return([galaxy_z[0],galaxy_z[4],galaxy_z[5],galaxy_z[6],'g141'])

def Main():
    file=pd.read_csv(str(raw_input("path to file: ")))
    output=open(str(raw_input("path and name of output file: ")),'w')
    id=file['galaxy_id']
    g102_z=file['g102_z']
    g102_uh=file['g102_uh']
    g102_ul=file['g102_ul']
    g141_z=file['g141_z']
    g141_uh=file['g141_uh']
    g141_ul=file['g141_ul']
    output.write('galaxy_id'+'\t'+'z_best'+'\t'+'unc_high'+'\t'+'unc_low'+'\t'+'grism'+'\n')
    for entry in range(len(id)):
        galaxy_z=[]
        galaxy_z.append(id[entry])
        galaxy_z.append(g102_z[entry])
        galaxy_z.append(g102_uh[entry])
        galaxy_z.append(g102_ul[entry])
        galaxy_z.append(g141_z[entry])
        galaxy_z.append(g141_uh[entry])
        galaxy_z.append(g141_ul[entry])
        if Comparator(galaxy_z):
            result=Tester(galaxy_z)
        else:
            result=[galaxy_z[0],galaxy_z[1],galaxy_z[2],galaxy_z[3],'-99']
        for entry in range(len(result)):
            output.write(str(result[entry])+'\t')
        output.write('\n')
    output.close()

Main()
