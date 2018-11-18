#!/usr/bin/python
###############################################################################
# Script that calls CDO linux command to calculate 
# the annual anomalies with respect to the long-term climatology.
###############################################################################

import os
#import sys
#sys.path.append("./modules")
from cmip5 import *

def calc_ano(scen,model,run,v,startyr,endyr,realm=None):
    """Subtracts the climatology from the annual mean data using CDO.
    
    Input variables:
        scen,model,run,v: strings indicating the scenario, 
            ensemble member run, and the variable name.
            These variables are used to form the netcdf file names
            that are processed with cdo.
        startyr, endyr: integer numbers for the first and last year (climatology file)
        realm: optional string argument corresponding to the 
            variable processed that is used for the subfolder structure
            of the CMIP5 model

        
    """
    app="ano" # app is used in the output file name
    model_scen=TRANSLATE[scen]['scen']
    model_time=TRANSLATE[scen]['time']
    clim_scen=TRANSLATE['historical']['scen']
    clim_time=TRANSLATE['historical']['time']
     # adjust outpath to the subfolder structure 
    if realm != None:
        subdir_out=model_scen+"/"+realm+"/"+v+"/"
        subdir_clim=clim_scen+"/"+realm+"/"+v+"/"
    else:
        subdir_out=model_scen+"/"+v+"/"
        subdir_clim=clim_scen+"/"+v+"/"
    
    infile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann.nc"
    infile_clim=model+"_"+clim_scen+"_"+v+"_"+clim_time+"_"+run+"_ann_clim.nc"
    # OUTPATH: Input path and output path are the same.
    outfile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+\
    "_ann_"+app+".nc" 
    cdo="cdo -v sub "+OUTPATH+subdir_out+infile+" "+OUTPATH+subdir_clim+infile_clim+" "+\
    OUTPATH+subdir_out+outfile
    print(cdo)
    os.system(cdo)
    print ("Infile:      "+infile)
    print ("Climatology: "+infile_clim)
    print ("Outfile:     "+outfile)
    print ("Folder:      "+OUTPATH+subdir_out)
    return

# Loop over scenarios
iscen=0
for scen in SCENARIOLIST:
    print ("scenario: "+scen)
    nmodel=0
    for model in MODELLIST:
        for run in ENSEMBLELIST:
            i=0
            for v in VARLIST:
                calc_ano(scen,model,run,v,START,END,realm='ocn')
                i+=1
        nmodel+=1
    print ("----------------------------------------------------------")
    print ("stats for simulations "+scen+" : variable "+v)
    print ("models: "+str(nmodel)+" variables: "+str(i))
    iscen+=1


 
