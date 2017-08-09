# -*- coding: utf-8 -*-
"""
Created on Tue May  5 15:40:33 2015

@author: donald
"""
#concatenates result of concatenator1 with RF color uds file
firstconcat='concatenated.txt'
udsRF='uds_3dhst.v4.2.master.RF'
out='concatenated2.txt'

firstc=open(firstconcat,'r')
udsrest=open(udsRF,'r')
output=open(out,'w')

uds_id=[]
udslist=[]
d4klist=[]
d4k_id=[]
counter=0
for line in udsrest: #strips off header and column titles of uds output
    if counter < 27:
        counter+=1
    else: 
        splitit=line.split()
        uds_id.append(splitit[0])
        udslist.append(line)
for line in range(len(udslist)):
    udslist[line]=udslist[line].strip('\n')
counter2=0
for line in firstc: #processes d4k output
    if counter2 < 1:
        counter2+=1
    else:
        splitit=line.split()
        namestring=splitit[0]
        namestring=namestring.split('_')
        d4k_id.append(namestring[1])
        d4klist.append(line)
for line in range(len(d4klist)): #compares object IDs
    d4klist[line]=d4klist[line].strip('\n')
for entry in range(len(d4k_id)):
    for entry2 in range(len(uds_id)):
        if d4k_id[entry]==uds_id[entry2]: #concatenates if match
            outstring=d4klist[entry]+'\t'+udslist[entry2]+'\n'
            output.write(outstring)
    
d4k.close()
uds.close()
output.close()
