#!/usr/bin/python
###############################################################################
# PCA (EOF) analysis specific for the North Pacific SST anomalies
# for the analysis of the PDO
# Select North Pacific domain and apply PCA on the residual
# (no latitude weighting at the moment)
###############################################################################
# Results are saved in netcdf format:
# Eigenvectors (PCA pattern) in eof.nc
# PC time series and explained variance in pc.nc
###############################################################################
# HISTORY:
# 2018-07-19:OET: Corrected in function save_results the attributes 
#   for variable eof in netcdf output.
#   Updated the regional domain selection: lat,lon boundaries are now 
#   added to the cmip5.py module as a tuple (lonw,lone,lats,latn) 
#   REGION_PDO.    
###############################################################################

import xarray
import numpy as np
import os
from sklearn.decomposition import PCA
from cmip5 import *

def field2matrix(x3d):
    """Convert shape of 3dim array into 2dim array.

    It also removes grid cells with nan values.
    Input array dimensions are assumed to be time,lat,lon
    Output array dimensions are  time, lat*lon

    An array with the valid grid point locations is returned,too.
    This array is needed for the proper conversion back to the 3-dim array.
    """
    dim3d=np.shape(x3d)
    x2d=np.reshape(x3d,(dim3d[0],dim3d[1]*dim3d[2]))
    is_nan=np.any(np.isnan(x2d),0) # check for nan grid points
    is_valid=~is_nan
    ihelp=np.arange(0,len(is_valid),1)
    valid_index=ihelp[is_valid]
    return x2d[:,is_valid], valid_index

def matrix2field(x2d,nlat,nlon,valid_index):
    """Convert shape of 2dim array into 3dim array.

    Input parameter valid_index is an array with the valid grid point locations 
    This array is needed for the proper conversion back to the 3-dim array.
    It is returned by the function field2matrix. This function is the inverse
    reshaping process.
    """
    # inverse transform
    # first expand
    buffer=np.empty(shape=(len(x2d[:,0]),nlat*nlon))
    buffer[:]=np.nan
    i=0
    while i< len(valid_index):
        buffer[:,valid_index[i]]=x2d[:,i]
        i+=1
    return np.reshape(buffer,(len(x2d[:,0]),nlat,nlon))


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
    rhelp=np.dot(vx[is_use],ve[is_use])/np.sqrt(np.dot(ve[is_use],ve[is_use]))
    return rhelp

def save_result(eof,pc,time,lat,lon,expvar,copy_from_source,dflt_units='k'):
    """Saves the results from the EOF analysis in netcdf files

    Input parameters:

        eof: field (3dim array) with eofs (usually only leading modes)
        pc: corresponding principal component time series
        time: coordinates from input netcdf file
        lat,lon: the sub-domain lat, lon coordinates
        expvar: array with explained variance (fractions)
        copy_from_source: the field variable from the source  netcdf file
            The copy_from_source provides a netcdf source file (the input field
            data file to copy the information about dimensions, variables, units etc.
    """
    ncsrc=copy_from_source # use shorter variable name
    lev=np.arange(1,(len(eof[:,0,0])+1),1)
    xeof=xarray.DataArray(eof,coords=[lev,lat,lon],dims=['lev','lat','lon'])
    xeof.name='eof'
    # 2018-07-19 corrected long_name and units attribute for eofs
    xeof.attrs['long_name']="eigenvector" # check if that is right
    xeof.attrs['units']='1' # eigenvectors of unit length
    ds1=xarray.Dataset({'eof':xeof})
    print(ds1)
    ds1.to_netcdf('eof.nc',format="NETCDF4")

    # issues with level dimension in ferret so write to separate file
    # but include expvar in here
    xpc=xarray.DataArray(pc,coords=[time,lev],dims=['time','lev'])
    xpc.name='pc'
    xpc.attrs['long_name']='projection index'
    try:
        xpc.attrs['units']=ncsrc.units #
    except:
        xpc.attrs['units']=dflt_units
    xexpvar=xarray.DataArray(expvar,coords=[lev],dims=['lev'])
    xexpvar.name='expvar'
    xexpvar.attrs['long_name']='explained variance'
    xexpvar.attrs['units']='percent'
    ds2=xarray.Dataset({'pc':xpc,'expvar':xexpvar})
    print(ds2)
    ds2.to_netcdf('pc.nc',format="NETCDF4")
    return ds1,ds2


# APPLIED OPERATION
# (used in output file name, added just before input file name '*.nc')
app="pca"

###############################################################################
# If RESID is True then the input data is
# the linear regression residual
# (removed global mean trend)
# RESID=False uses anomaly data
# (global mean trend signal included)
###############################################################################
RESID=True

realm='ocn' # or set to None, depending of sub-folder structure
iscen=0
# LOOP OVER SCENARIOS: (usually only historical, but keep loop structure)
for scen in ['historical']:
    nmodel=0
    i=-1
    for model in MODELLIST:
        for run in ENSEMBLELIST:
            for v in VARLIST:
                print (v)
                model_scen=TRANSLATE[scen]['scen']
                model_time=TRANSLATE[scen]['time']
                # adjust outpath to the subfolder structure 
                if realm != None:
                    subdir_out=model_scen+"/"+realm+"/"+v+"/"
                else:
                    subdir_out=model_scen+"/"+v+"/"
                # 3-dim field
                if RESID:
                    infile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann_ano_resid.nc"
                    outfile_eof=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann_ano_resid_eof.nc"
                    outfile_pc=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann_ano_resid_pc.nc"
                else:
                    infile=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann_ano.nc" 
                    outfile_eof=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann_ano_eof.nc"
                    outfile_pc=model+"_"+model_scen+"_"+v+"_"+model_time+"_"+run+"_ann_ano_pc.nc"
                ### open the data sets ###
                nc1=xarray.open_dataset(OUTPATH+subdir_out+infile)
                ntime1=nc1.time.size
                fielddata=nc1[v].values[:]
                ###nc2=xarray.open_dataset(OUTPATH+infile)
                #################################################
                # select North Pacific Domain and apply PCA
                # to the residuals
                #################################################
                sellon=REGION_PDO[0:2]
                sellat=REGION_PDO[2:4]
                is_lon=np.logical_and(nc1.lon.values>=sellon[0],nc1.lon.values<=sellon[1])
                nlon=np.sum(is_lon)
                is_lat=np.logical_and(nc1.lat.values>=sellat[0],nc1.lat.values<=sellat[1])
                nlat=np.sum(is_lat)
                buffer=fielddata[:,:,is_lon]
                res_npac=buffer[:,is_lat,:]
                # need a 2dim array with time and grid coordinate as 2nd dim
                # and have to get rid of grid points with nan
                x2d,valid_index=field2matrix(res_npac)
                #################################################
                # PCA analysis
                #################################################
                nmodes=10
                print ("calculate PCA ...")
                pca = PCA().fit(x2d)
                eof= pca.components_[0:nmodes,:] # leading modes
                # 1s EOF should represent PDO mode
                field_eof=matrix2field(eof,nlat,nlon,valid_index)
                #################################################
                # Projection of field data onto eigenvector
                #################################################
                t=0
                ntime=len(res_npac[:,0,0])
                pc=np.zeros((ntime,nmodes))
                while t<ntime:
                    m=0
                    while m<nmodes:
                        pc[t,m]=proj_field(res_npac[t,:,:],field_eof[m,:,:])
                        m+=1
                    t+=1
                #################################################
                # savc results into netcdf file
                #################################################
                ds1,ds2=save_result(eof=field_eof,pc=pc,\
                time=nc1.time,lat=nc1.lat[is_lat],\
                lon=nc1.lon[is_lon],\
                expvar=pca.explained_variance_[0:nmodes],\
                copy_from_source=nc1[v])

                if False:
                    fig,ax=plt.subplots(2,2)
                    ax[0,0].bar(range(10),pca.explained_variance_[0:10]/np.sum(pca.explained_variance_)*100)
                    ax[0,0].set_xlabel('PCA mode #')
                    ax[0,0].set_ylabel('explained variance [%]')
                    ax[1,0].contourf(nc1.lon[is_lon],nc1.lat[is_lat],field_eof[0,:,:],cmap=plt.cm.coolwarm)
                    plt.show()
                i=i+1
                # renaming the files eof.nc and pc.nc
                #
                print ("Input file for PCA (EOF) analysis: ")
                print(OUTPATH+subdir_out+infile)
                print ("EOF pattern written to:")
                print (OUTPATH+subdir_out+outfile_eof)
                print ("PC time series and explained variances written to:")
                print (OUTPATH+subdir_out+outfile_pc)
                os.system("mv eof.nc "+OUTPATH+subdir_out+outfile_eof)
                os.system("mv pc.nc "+OUTPATH+subdir_out+outfile_pc)
            nmodel+=1
    iscen+=1
print ("done")




















