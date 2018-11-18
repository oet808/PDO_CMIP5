#!/usr/bin/python
###############################################################################
# Calculates the global mean using 'fldmean' operation in the CDO
# linux command (using annual mean data)
# The resulting netcdf file contains a single time series
# (but lon, lat coordinate dimensions will still exist in the output file)
###############################################################################

import os
#import sys
#sys.path.append("./modules")
from cmip5 import *

def global_mean(scen,model,run,v,realm='None'):
    """Calculates the global mean (time series) using CDO.
    
    Input variables:
        scen,model,run,v: strings indicating the scenario, 
            model,ensemble member run, and the variable name.
            These variables are used to form the netcdf file names
            that are processed with cdo.
        realm: optional string argument corresponding to the 
            variable processed that is used for the subfolder structure
            of the CMIP5 model.
    """
    app="fldmean" # app is used in the output file name
    model_scen=TRANSLATE[scen]['scen']
    model_time=TRANSLATE[scen]['time']
    # adjust outpath to the subfolder structure 
    if realm != None:
        subdir_out=model_scen+"/"+realm+"/"+v+"/"
    else:
        subdir_out=model_scen+"/"+v+"/"
    
    infile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann_ano.nc"
    # OUTPATH: Input path and output path are the same.
    outfile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+\
    "_ann_ano_"+app+".nc" 
    cdo="cdo  -v fldmean "+\
    OUTPATH+subdir_out+infile+" "+OUTPATH+subdir_out+outfile
    print(cdo)
    os.system(cdo)
    print ("Infile:  "+infile)
    print ("Outfile: "+outfile)
    print ("Folder:  "+OUTPATH+subdir_out)
    return

# Loop over scenarios
iscen=0
for scen in SCENARIOLIST:
    print ("scenario: "+scen)
    nmodel=0
    for model in MODELLIST:
        print ("model: "+model)
        for run in ENSEMBLELIST:
            i=0
            for v in VARLIST:
                global_mean(scen,model,run,v,realm='ocn')
                i+=1
        nmodel+=1
    print ("----------------------------------------------------------")
    print ("stats for simulations "+scen+" : variable "+v)
    print ("models: "+str(nmodel)+" variables: "+str(i))
    iscen+=1



 
