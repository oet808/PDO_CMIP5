#!/usr/bin/python
###############################################################################
# calculate projection index for a time-varying field
# using eofs (or any other pattern) as vectors for the projection
# This script works with the PCA results of the North Pacific domain.
# This script uses the model's eof projection 
# vector (as the defaul PDO pattern). 
###############################################################################
# Results: netcdf time series output
###############################################################################

import xarray
import numpy as np
import os
#import sys
#sys.path.append("./modules")
from cmip5 import *


def proj_field(x,e):
    """Vector dot product of field pattern with projection pattern.
    
    Project field x onto field e using vector projection (dot product).
    Input assumed 2dim lat,lon.
    Currently no area (latitude weighting) supported.
    """
    ndim=np.shape(x)
    vx=np.reshape(x,np.size(x))
    ve=np.reshape(e,np.size(e))
    # must remove nan values from arrays before np.dot function
    is_x=~np.isnan(vx)
    is_e=~np.isnan(ve)
    is_use=np.logical_and(is_x,is_e)
    ve=np.reshape(e,np.size(x))
    rhelp=np.dot(vx[is_use],ve[is_use])/np.sqrt(np.dot(ve[is_use],ve[is_use]))
    return rhelp

def save_result(x,time,lev,copy_from_source,dflt_units='k'):
    """Saves results from projection in netcdf output format.
    
    Input parameters:
        x: projection indices (2dim array with time,mode) 
        time: coordinates from input netcdf file
        lev: level coordinates (PCA modes)
        copy_from_source: the field variable from the source  netcdf file 
     
    The copy_from_source provides a netcdf source file (the input field
    data file to copy the information about dimensions, variables, units etc.
    
    Output contains the projection index time series.
    """
    ncsrc=copy_from_source # use shorter variable name
    lev=np.arange(1,(len(x[0,:])+1),1)
    xproj=xarray.DataArray(x,coords=[time,lev],dims=['time','lev'])
    xproj.name="proj"
    xproj.attrs["long_name"]="projection index"
    try:
        xproj.attrs['units']=ncsrc.units # check if that is right
    except:
        print("save_result: could not find attribute 'units' for copying")
        print("assign default units to variable: "+dflt_units)
        xproj.attrs['units']=dflt_units # eigenvectors of unit length
        xproj.attrs['info']="projection onto ensemble mean EOF pattern in eof_ens_mean.nc"
    ds=xarray.Dataset({'proj':xproj})
    ds.to_netcdf('proj.nc',format="NETCDF4")
    return ds

# APPLIED OPERATION 
# (used in output file name, added just before input file name '*.nc')
app="pdo_proj"

 

###############################################################################
# If RESID is True then the input data is
# the linear regression residual
# (removed global mean trend)
# RESID=False uses anomaly data
# (global mean trend signal included)
###############################################################################
RESID=True

realm='ocn' # or set to None, depending of sub-folder structure

# LOOP OVER SCENARIOS
iscen=-1
for scen in SCENARIOLIST:
    iscen=iscen+1
    nmodel=0
    i=-1
    for model in MODELLIST:
        print ("model: "+model)
        for run in ENSEMBLELIST:
            for v in VARLIST:
                # 3-dim field
                # EOF projection eignevectors 
                # The projection vector is in standard application from historical scenario 
                # eof_scen eof_time is set as default to the historical scenario
                eof_scen=TRANSLATE['historical']['scen']
                eof_time=TRANSLATE['historical']['time']
                model_scen=TRANSLATE[scen]['scen']
                model_time=TRANSLATE[scen]['time']
                # adjust outpath to the subfolder structure 
                if realm != None:
                    subdir_out=model_scen+"/"+realm+"/"+v+"/"
                    subdir_eof=eof_scen+"/"+realm+"/"+v+"/"
                else:
                    subdir_out=model_scen+"/"+v+"/"
                    subdir_eof=model_scen+"/"+v+"/"
                
                infile_eof=model+"_"+eof_scen+"_"+v+"_"+eof_time+"_"+run+'_ann_ano_resid_eof.nc'
                if RESID:
                    infile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann_ano_resid.nc"
                    outfile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann_ano_resid_"+app+".nc"
                else:
                    infile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann_ano.nc" 
                    outfile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann_ano_"+app+".nc"
                print("field data: "+OUTPATH+subdir_out+infile)
                print("eigenvectors from "+OUTPATH+subdir_eof+infile_eof)
                print("output file: "+OUTPATH+subdir_out+outfile)
                print ("call function to read the netcdf files")
                ### open the data sets ###
                nc1=xarray.open_dataset(OUTPATH+subdir_out+infile)
                ntime1=nc1.time.size
                field=(nc1[v].values[:]).squeeze()  # save use for annual anomaly data
                nc2=xarray.open_dataset(OUTPATH+subdir_eof+infile_eof)
                eof=(nc2['eof'].values[:])
                nmodes=len(eof[:,0,0])
                #######################################################################
                # select North Pacific Domain and apply PCA
                # to the residuals
                #######################################################################
                sellon=REGION_PDO[0:2]
                sellat=REGION_PDO[2:4]
                is_lon1=np.logical_and(nc1.lon.values>=sellon[0],nc1.lon.values<=sellon[1])
                nlon1=np.sum(is_lon1)
                is_lat1=np.logical_and(nc1.lat.values>=sellat[0],nc1.lat.values<=sellat[1])
                nlat1=np.sum(is_lat1)
                buffer=field[:,:,is_lon1]
                field_npac=buffer[:,is_lat1,:]
                # make this check here, in case we combine with other domain
                # sizes
                is_lon2=np.logical_and(nc2.lon.values>=sellon[0],nc2.lon.values<=sellon[1])
                nlon2=np.sum(is_lon2)
                is_lat2=np.logical_and(nc2.lat.values>=sellat[0],nc2.lat.values<=sellat[1])
                nlat2=np.sum(is_lat2)
                buffer=eof[:,:,is_lon2]
                field_eof=buffer[:,is_lat2,:]

                #######################################################################
                # Projection of field data onto eigenvector
                # (1st EOF should represent PDO mode)
                #######################################################################
                t=0
                ntime=len(field_npac[:,0,0])
                proj=np.zeros((ntime,nmodes))
                while t<ntime:
                    m=0
                    while m <nmodes:
                        proj[t,m]=proj_field(field_npac[t,:,:],field_eof[m,:,:])
                        m+=1
                    #print(t)
                    t=t+1
                ds=save_result(proj,nc1.time,nc2.lev,copy_from_source=nc1[v]) 
                if False:
                    fig,ax=plt.subplots(2,2)
                    ax[0,0].plot(nc1['time'],proj[:,MODE_PDO])
                    ax[0,0].set_xlabel('PCA mode #')
                    ax[0,0].set_ylabel('projection index')
                    ax[1,0].contourf(nc2.lon[is_lon2],nc2.lat[is_lat2],field_eof[MODE_PDO,:,:],cmap=plt.cm.coolwarm)
                    plt.show()      
                i=i+1
                os.system("mv proj.nc "+OUTPATH+subdir_out+outfile)
                print ("outfile: "+OUTPATH+subdir_out+outfile)
        nmodel+=1
print ("done")


















