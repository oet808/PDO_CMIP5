#!/usr/bin/python
###############################################################################
# calculate the linear regression
# field using a netcdf 3-dim (time,lat,lon)
# and 1-d (time) netcdf index series
# time axis does not have to match, but the length
# must match.
# Returns the following fields: 
# intercept, slope, r-value (2dim lat,lon)
# and the residual field (3-dim, time,lat,lon)
# KNOWN PROBLEMS:
# the input data have a non-conformal time coordinate system
# and the output with xarray cannot handle that information
#
###############################################################################

import os
import xarray
import numpy as np
from scipy.stats import linregress
#import sys
#sys.path.append("./modules")
from cmip5 import *

def save_result(scen,run,varname,x,time,lat,lon,copy_from_source,\
                dflt_units='k',realm=None):
    """saves results in netcdf output format
    input parameters:
        x: field (3dim array) (residuals from linear regression)
            variable name for  netcdf file variable
        time: coordinates from input netcdf file
        lat,lon: the sub-domain lat, lon coordinate
        copy_from_source: the field variable from the source  netcdf file.
           The copy_from_source provides a netcdf source file (the input field
           data file to copy the information about dimensions, variables, units etc.)
       
        realm: optional string argument corresponding to the 
            variable processed that is used for the subfolder structure
            of the CMIP5 model.
    """

    app="resid"
    # OUTPATH: Input path and output path are the same.
    model_scen=TRANSLATE[scen]['scen']
    model_time=TRANSLATE[scen]['time']
    # adjust outpath to the subfolder structure 
    if realm != None:
        subdir_out=model_scen+"/"+realm+"/"+v+"/"
    else:
        subdir_out=model_scen+"/"+v+"/"

    outfile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+\
    "_ann_ano_"+app+".nc" 

    ncsrc=copy_from_source # use shorter variable name
    lev=np.arange(1,(len(x[:,0,0])+1),1)
    xeof=xarray.DataArray(x,coords=[time,lat,lon],dims=['time','lat','lon'])
    xeof.name=varname
    try:
        xeof.attrs['long_name']=ncsrc.long_name # check if that is right
    except:
        print("save_result: could not find attribute 'long_name' for copying")
        xeof.attrs['units']='1' # eigenvectors of unit length
    ds=xarray.Dataset({varname:xeof})
    ds.to_netcdf(OUTPATH+subdir_out+outfile,format="NETCDF4")
    print ("Output file with residuals:")
    print (OUTPATH+subdir_out+outfile)
    print(ds)
    return ds


def linreg(scen,model,run,v,realm=None):
    """calculated the linear regression at each grid point with the time series and saves the residual
    variability in a netcdf file.
    
    Input variables:
        scen,model,run,v: strings indicating the scenario, 
            model,ensemble member run, and the variable name.
            These variables are used to form the netcdf file names
            that are processed with cdo.
        realm: optional string argument corresponding to the 
            variable processed that is used for the subfolder structure
            of the CMIP5 model.
    Dependencies: packages xarray, scipy.stats, and numpy
    """
    app="resid"
    # 3-dim field
    model_scen=TRANSLATE[scen]['scen']
    model_time=TRANSLATE[scen]['time']
    # adjust outpath to the subfolder structure 
    if realm != None:
        subdir_out=model_scen+"/"+realm+"/"+v+"/"
    else:
        subdir_out=model_scen+"/"+v+"/"

    infile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann_ano.nc"
    # time series
    infile_ts=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann_ano_fldmean.nc"
    # output file see function save_result        
   
    print ("read the netcdf files ...")
    print ("Field data  : "+OUTPATH+subdir_out+infile)
    print ("Time series : "+OUTPATH+subdir_out+infile_ts)
    ### open the data sets ###
    nc1=xarray.open_dataset(OUTPATH+subdir_out+infile)
    ntime1=nc1.time.size
    fielddata=(nc1[v].values[:]).squeeze()
    nc2=xarray.open_dataset(OUTPATH+subdir_out+infile_ts)
    ntime2=nc2.time.size
    x=(nc2[v].values[:]).squeeze()
    if ntime1 != ntime2:
        print ("Error: input files do not have same number of samples in time dimension")
        print("fielddata:")
        print(type(fielddata))
        print(np.shape(fielddata))
        print("time series:")
        print(type(x))
        print(np.shape(x))
    else:
    ### apply linregress to
        print("apply linear regression and remove the signal (saving residual variability) ...")
        print(type(fielddata))
        print(np.shape(fielddata))
        print("time series:")
        print(type(x))
        print(np.shape(x))
        a=np.zeros(shape=np.shape(fielddata[0,:,:]))
        b=np.zeros(shape=np.shape(a))
        r=np.zeros(shape=np.shape(a))
        res=np.zeros(shape=np.shape(fielddata))
        j=0
        jmax=np.shape(fielddata[0,:,0])[0] # [0] helps to get number instead tuple
        kmax=np.shape(fielddata[0,0,:])[0]
        while j<jmax:
            k=0
            while k<kmax:
                b[j,k],a[j,k],r[j,k],pval,serr=linregress(x,fielddata[:,j,k])
                res[:,j,k]=fielddata[:,j,k]-(a[j,k]+b[j,k]*x)
                #print(j,k)
                k=k+1
            # end loop k
            j=j+1
        # end loop j
        ds=save_result(scen,run,v,res,time=nc1.time,\
        lat=nc1.lat,\
        lon=nc1.lon,\
        copy_from_source=nc1[v],realm='ocn')

                
# Loop over scenarios
iscen=0
for scen in SCENARIOLIST:
    print ("scenario: "+scen)
    nmodel=0
    for model in MODELLIST:
        for run in ENSEMBLELIST:
            i=0
            for v in VARLIST:
                linreg(scen,model,run,v,realm='ocn')
                i+=1
        nmodel+=1
    print ("----------------------------------------------------------")
    print ("stats for simulations "+scen+" : variable "+v)
    print ("models: "+str(nmodel)+" variables: "+str(i))
    iscen+=1
