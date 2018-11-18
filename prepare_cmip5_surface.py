#!/network/rit/lab/snowclus/anaconda31/bin/python
# 2018-07-09 script based on 
# CMIP_ANALYSIS/prepare_cmip5_surface.py
# adjusted for remote OPENDAP access
# of TOS from CMIP5 models stored at APDRC
#
import os

OPENDAP_PATH="http://apdrc.soest.hawaii.edu:80/dods/public_data/CMIP5/"
WORKHOST="snow"

SCENARIOLIST=["historical"] #,"rcp85","rcp45"]
#SCENARIOLIST=["rcp45"]
MODELLIST=["CMCC-CM"]
#MODELLIST=["ACCESS1-0", "ACCESS1-3","CESM1-CAM5","ACCESS1-0"]
# output data path
# TODO: decide whether all scenarios in one
# or for each scenario into their own DERIVED folder
# Anyways have to change this, right now all goes into HIST 
OUTPATH="/data/elisontimm_scr/DATA/CMIP5/HIST/DERIVED/"

VARLIST=["tos"]

# standard grid for all models
OUTGRID="/network/rit/lab/elisontimmlab_rit/DATA/NCEP/gridfile.nc"
iscen=-1
RUN="r1i1p1_1"


# LOOP OVER SCENARIOS
for SCENARIO in SCENARIOLIST:
    iscen=iscen+1
    # LOOP OVER MODELS
    nmodel=0
    for MODEL in MODELLIST:
        i=-1
        for VAR in VARLIST:
            SOURCE=OPENDAP_PATH+"/"+SCENARIO+"/"+VAR+"/"+MODEL+"_"+RUN
            print("process model data from source "+SOURCE)
            cmd="rm check_units+"+SCENARIO+"_"+VAR+".tmp"
            os.system(cmd)
            i=i+1
            # check units
            cmd="ncdump -h "+SOURCE+" | grep -i "+VAR+":units >> check_units+"+SCENARIO+"_"+VAR+".tmp"
            os.system(cmd)
            # extract variable
            #cdo="cdo -selvar,"+VAR+" "+SOURCE+" buffer"+str(ifile)+".tmp"
            #print cdo
            #os.system(cdo)
           

            # remap to 2.5 x 2.5 NCEP grid
            cdo="cdo -remapbil,"+OUTGRID+" "+SOURCE+" remap.nc"
            print (cdo)
            os.system(cdo)
            outfile="cmip5_"+SCENARIO+"_"+VAR+"_"+MODEL+"_"+RUN+".nc"
            print (outfile)
            cmd="cp -p remap.nc "+OUTPATH+outfile
            os.system(cmd)
            os.system("rm buffer*.tmp buffer.nc remap.nc")
    nmodel+=1
    print ("----------------------------------------------------------")
    print ("stats for CMIP5 simulations "+SCENARIO+" : variable "+VAR)
    print ("models: "+str(nmodel))
print ("done")



    

 
