###############################################################################
# Module that contains the CMIP5 
# multi-model ensemble specifications
###############################################################################
"""Declarations of default variables for the CLENS ensemble. 
The test version does include a single scenario and single ensemble run.
"""

# Path to the directory with the source netcdf files
DPATH="/network/rit/lab/elisontimmlab_rit/kf835882/python" # must always end with '/'

# output data path
OUTPATH="/data/elisontimm_scr/DATA/CMIP5/IPRC/" # must always end with '/'

# CMIP5 scenarios
SCENARIOLIST=["historical","rcp85"]

# multi-model ensemble (like CMIP5) should use MODELLIST
# to iterate over model members
MODELLIST=["ACCESS1-0","ACCESS1-3"]

# realm (model component "atm","ocn")
REALMLIST= ["ocn"]
# only SST (TOS) processed here, but can iterate over several variables in a file
VARLIST=["tos"]

# standard grid for all models
# This one is a 2.5 x 2.5 regular lon-lat grid
OUTGRID="/network/rit/lab/elisontimmlab_rit/DATA/NCEP/gridfile.nc"


###############################################################################
# CMIP5 model specific variables
###############################################################################

ENSEMBLELIST=['r1i1p1_1']

###############################################################################
# I use this dictionary to 'translate' the CMIP5 
# standard naming convention so that the code structure
# looks very much like the code for other ensemble
# analysis code (e.g. CLENS)
# for multi-model ensemble data processing. 
# Use of nested dictionaries allows for additional 
# 'translations'
###############################################################################
TRANSLATE={'historical':{'scen':'historical','time':'',"first_year":1901},\
                    'rcp85':{'scen':'rcp85','time':'',"first_year":2006}}


###############################################################################
# Specific settings for data processing with CDO
###############################################################################

# APPLY time coordinate correction to when calculating 
# annual mean data from monthly data
CORRECT_ANN_CALENDAR=True 

# climatology: start and end years for the averaging
START=1975
END=2005

###############################################################################
# Define lat-lon region for spatially restricted analyses
###############################################################################
# For the PDO analysis (PCA and projection index)
REGION_PDO=(110.0,260.0,20.0,70.0)
# PCA (EOF) mode number for PDO (default value is first mode is PDO)
MODE_PDO=0 # first PCA mode should be PDO in models
# Lowpass filter cutoff frequency: f=1/(time steps)
LPCUTOFF=1./15.0 
