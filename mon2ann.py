#!/usr/bin/python
# mon2ann updated to work with CMIP5
# multi-model ensemble
# code based on mon2ann for CLENS ensemble

#!/usr/bin/python
###############################################################################
# Script that calls CDO
# linux command to calculate annual mean
# This is the unweighted mean (Jan, Feb, Mar, Apr hav same weight)
# IMPORTANT: THE CLENS monthly mean data have a time axis shifted 
# by one month! Feb in year i is the monthly mean of January year i
# Dec is Nov mean, and Jan year i+1 is the average of Dec year i!
###############################################################################

import os
#import sys
#sys.path.append("./modules")
from cmip5 import *


def calc_ann_mean(scen,run,v,realm=none):
    """calculates annual mean from monthly mean data using CDO.
    
    Input variables:
        scen,run,v are strings indicating the scenario, 
        ensemble member run, and the variable name.
        These variables are used to form the netcdf file names
        that are processed with cdo.
        realm is an optional string argument corresponding to the 
        variable processed that is used for the subfolder structure
        of the CMIP5 model.
    """
    app="ann" # app is used in the output file name
    model_scen=TRANSLATE[scen]['scen']
    model_time=TRANSLATE[scen]['time']
    infile="cmip5_"+model_scen+"_"+v+"_"+MODEL+"_"+v+"_"+run+".nc"
    # Input path and output path are the same 
    # for input files that are itself not the 
    # original data files

    # adjust outpath to the subfolder structure 
    if realm != none:
        subdir_out=model_scen+"/"+realm+"/"
    else:
        subdir_out=model_scen+"/"
    outfile=MODEL+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+\
    "_"+app+".nc" 
    if CORRECT_ANN_CALENDAR:
        first_year=str(TRANSLATE[scen]['first_year'])
        os.system("rm buffer.nc buffer2.nc")
        cdo="cdo -v -timselmean,12 "+OUTPATH+sudir_out+infile+" buffer.nc"
        print(cdo)
        os.system(cdo)
        print("use cdo to overwrite time dimension / correct the calendar")
        cdo="cdo -v -settaxis,"+first_year+"-01-01,00:00:00,365day buffer.nc buffer2.nc\n"
        cdo=cdo+"cdo  -setcalendar,standard buffer2.nc "+OUTPATH+subdir_out+outfile
        print(cdo)
        os.system(cdo)
    else:
        cdo="cdo -v -timselmean,12 "+OUTPATH+infile\
        +" "+OUTPATH+subdir_out+outfile
        print(cdo)
        os.system(cdo)
    
    print ("Infile: "+infile)
    print ("Outfile:"+outfile)
    print ("Folder: "+OUTPATH)
    return


# Loop over scenarios
iscen=0
for scen in SCENARIOLIST:
    nmodel=0
    for run in ENSEMBLELIST:
        i=0
        for v in VARLIST:
            calc_ann_mean(scen,run,v)
            i+=1
    nmodel+=1
    print ("----------------------------------------------------------")
    print ("stats for simulations "+scen+" : variable "+v)
    print ("models: "+str(nmodel)+" variables: "+str(i))
    iscen+=1


 
 
 
