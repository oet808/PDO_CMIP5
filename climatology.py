#!/usr/bin/python
###############################################################################
# Script that calls CDO
# linux command to calculate the long-term climatology
# (from annual mean data)
###############################################################################

import os
#import sys
#sys.path.append("./modules")
from cmip5 import *

def calc_clim(scen,model,run,v,startyr,endyr,realm=None):
    """Calculates climatology from annual mean data using CDO.
    
    Input variables:
        scen,model,run,v: strings indicating the scenario, 
            model,ensemble member run, and the variable name.
            These variables are used to form the netcdf file names
            that are processed with cdo.
        startyr, endyr: integer numbers for the first and last year.
        realm: optional string argument corresponding to the 
            variable processed that is used for the subfolder structure
            of the CMIP5 model.
    """
    app="clim" # app is used in the output file name
    
    model_scen=TRANSLATE[scen]['scen']
    model_time=TRANSLATE[scen]['time']
    # adjust outpath to the subfolder structure 
    if realm != None:
        subdir_out=model_scen+"/"+realm+"/"+v+"/"
    else:
        subdir_out=model_scen+"/"+v+"/"
    infile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann.nc"
    # OUTPATH: Input path and output path are the same.
    outfile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+\
    "_ann_"+app+".nc"
    cdo="cdo -v timmean -selyear,"+str(startyr)+"/"+str(endyr)+" "+\
    OUTPATH+subdir_out+infile+" "+OUTPATH+subdir_out+outfile
    print(cdo)
    os.system(cdo)
    print ("Infile: "+infile)
    print ("Outfile:"+outfile)
    print ("Folder: "+OUTPATH)
    return

# Loop over scenarios (historical only, usually)
iscen=0
scen=TRANSLATE['historical']['scen']
nmodel=0
for model in MODELLIST:
    for run in ENSEMBLELIST:
        i=0
        for v in VARLIST:
            calc_clim(scen,model,run,v,startyr=START,endyr=END,realm="ocn")
            i+=1
    nmodel+=1
print ("----------------------------------------------------------")
print ("stats for simulations "+scen+" : variable "+v)
print ("models: "+str(nmodel)+" variables: "+str(i))
iscen+=1
