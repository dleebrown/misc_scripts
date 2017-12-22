"""little script to convert a deluxetable from a latex file to a csv file"""

import csv

readfile = open('tab3_2506.txt', 'r')
readfile = readfile.readlines()

outputlist = []
#strip out the control, header, and line break info
for line in readfile:
    if line[0] != '\\' and line[0] != '%':
        line = line.strip('\\\\\n')
        line = line.strip()
        line = line.replace(' & ',',')
        line = line.split(',')
        outputlist.append(line)

with open('latex_converted.csv', 'w') as outputfile:
    writeme = csv.writer(outputfile)
    writeme.writerows(outputlist)


