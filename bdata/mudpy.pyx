# Cython functions for running the cpp wrapper. 
# Derek Fujimoto
# July 2017
"""
Cython wrapper functions for friendly MUD file reading.
MUD source description can be found on the musr webpage: 
    http://musr.ca/mud/mud_friendly.html

Function list: 

    FILE IO
        open_read
        close_read
        
    RUN DESCRIPTION 
        get_description
        get_exp_number
        get_run_number
        get_elapsed_seconds
        get_start_time
        get_end_time
        get_title
        get_lab
        get_area
        get_method
        get_apparatus
        get_insert
        get_sample
        get_orientation
        get_das
        get_experimenter
    
    COMMENTS
        get_comments
        get_comment_prev
        get_comment_next
        get_comment_time
        get_comment_author
        get_comment_title
        get_comment_body
        
    HISTOGRAMS
        get_hists
        get_hist_type
        get_hist_n_bytes
        get_hist_n_bins
        get_hist_bytes_per_bin
        get_hist_fs_per_bin
        get_hist_t0_ps
        get_hist_t0_bin
        get_hist_good_bin1
        get_hist_good_bin2
        get_hist_background1
        get_hist_background2
        get_hist_n_events
        get_hist_title
        get_hist_sec_per_bin
        get_hist_data
        get_hist_data_pointer
        
    SCALARS
        get_scalers
        get_scaler_label
        get_scaler_counts
        
    INDEPENDENT VARIABLES
        get_ivars
        get_ivar_low
        get_ivar_high
        get_ivar_mean
        get_ivar_std
        get_ivar_skewness
        get_ivar_name
        get_ivar_description
        get_ivar_units

Derek Fujimoto 
July 2017
"""

import numpy as np
from cpython cimport array
import array


### ======================================================================= ###
# FILE IO
### ======================================================================= ###
cdef extern from "../mud_src/mud_friendly.c":
    int MUD_openRead(char* file_name, unsigned int* pType)
    void MUD_closeRead(int file_handle)

def open_read(file_name):
    """Returns file handle."""
    cdef unsigned int file_type = 0
    return <int> MUD_openRead(file_name.encode(),&file_type)
    
def close_read(file_handle):
    """Closes open file."""
    MUD_closeRead(file_handle)

### ======================================================================= ###
# RUN DESCRIPTION
### ======================================================================= ###
cdef extern from "../mud_src/mud_friendly.c":
    int MUD_getRunDesc(int fh, unsigned int* pType)
    int MUD_getExptNumber(int fh, unsigned int* pExpNumber)
    int MUD_getRunNumber(int fh, unsigned int* pRunNumber)
    int MUD_getElapsedSec(int fh, unsigned int* pElapsedSec)
    int MUD_getTimeBegin(int fh, unsigned int* pTimeBegin)
    int MUD_getTimeEnd(int fh, unsigned int* pTimeEnd)
    int MUD_getTitle(int fh, char* string, int strdim) 
    int MUD_getLab(int fh, char* string, int strdim)
    int MUD_getArea(int fh, char* string, int strdim)
    int MUD_getMethod(int fh, char* string, int strdim)
    int MUD_getApparatus(int fh, char* string, int strdim)
    int MUD_getInsert(int fh, char* string, int strdim)
    int MUD_getSample(int fh, char* string, int strdim)
    int MUD_getOrient(int fh, char* string, int strdim)
    int MUD_getDas(int fh, char* string, int strdim)
    int MUD_getExperimenter(int fh, char* string, int strdim)

def get_description(file_handle):
    """Returns int, related to file description."""
    cdef unsigned int type = 0
    MUD_getRunDesc(file_handle,&type)
    return <int>type

def get_exp_number(file_handle):
    """Returns int, experiment number."""
    cdef unsigned int expNumber = 0
    MUD_getExptNumber(file_handle,&expNumber)
    return <int>expNumber

def get_run_number(file_handle):
    """Returns int, run number."""
    cdef unsigned int runNumber = 0
    MUD_getRunNumber(file_handle,&runNumber)
    return <int>runNumber
    
def get_elapsed_seconds(file_handle):
    """Returns int, time elapsed during run in seconds."""
    cdef unsigned int time  = 0
    MUD_getElapsedSec(file_handle,&time)
    return <int>time
    
def get_start_time(file_handle):
    """Returns int, unix epoch timestamp associated with run start."""
    cdef unsigned int time  = 0
    MUD_getTimeBegin(file_handle,&time)
    return <int>time
    
def get_end_time(file_handle):
    """Returns int, unix epoch timestamp associated with run termination."""
    cdef unsigned int time  = 0
    MUD_getTimeEnd(file_handle,&time)
    return <int>time
    
def get_title(file_handle):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getTitle(file_handle,title,256)
    return <object>(title.decode('cp1252'))
    
def get_lab(file_handle):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getLab(file_handle,title,256)
    return <object>(title.decode('cp1252'))
 
def get_area(file_handle):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getArea(file_handle,title,256)
    return <object>(title.decode('cp1252'))
    
def get_method(file_handle):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getMethod(file_handle,title,256)
    return <object>(title.decode('cp1252'))
    
def get_apparatus(file_handle):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getApparatus(file_handle,title,256)
    return <object>(title.decode('cp1252'))
    
def get_insert(file_handle):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getInsert(file_handle,title,256)
    return <object>(title.decode('cp1252'))

def get_sample(file_handle):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getSample(file_handle,title,256)
    return <object>(title.decode('cp1252'))
    
def get_orientation(file_handle):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getOrient(file_handle,title,256)
    return <object>(title.decode('cp1252'))

def get_das(file_handle):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getDas(file_handle,title,256)
    return <object>(title.decode('cp1252'))

def get_experimenter(file_handle):
    """Returns python string. Max number of characters: 256. """
    cdef char title[256]
    MUD_getExperimenter(file_handle,title,256)
    return <object>(title.decode('cp1252'))
       
### ======================================================================= ###
# COMMENTS
### ======================================================================= ###
cdef extern from "../mud_src/mud_friendly.c":
    int MUD_getComments(int fh, unsigned int* pType, \
                        unsigned int* number_of_comments)
    int MUD_getCommentPrev(int fh, int num, unsigned int* pPrev )
    int MUD_getCommentNext(int fh, int num, unsigned int* pNext )
    int MUD_getCommentTime(int fh, int num, unsigned int* pTime )
    int MUD_getCommentAuthor(int fh, int num, char* author, int strdim )
    int MUD_getCommentTitle(int fh, int num, char* title, int strdim )
    int MUD_getCommentBody(int fh, int num, char* body, int strdim )
       
def get_comments(file_handle):
    """Returns numpy array of int32: [data type, number of comments]."""
    cdef unsigned int pType
    cdef unsigned int number_of_comments
    MUD_getComments(file_handle,&pType,&number_of_comments)
    return np.array([<int>pType,<int>number_of_comments])
    
def get_comment_prev(file_handle,comment_id_number):
    """Returns int, id of previous comment."""
    cdef unsigned int value
    MUD_getCommentPrev(file_handle,comment_id_number,&value)
    return <int>value

def get_comment_next(file_handle,comment_id_number):
    """Returns int, id of next comment."""
    cdef unsigned int value
    MUD_getCommentNext(file_handle,comment_id_number,&value)
    return <int>value

def get_comment_time(file_handle,comment_id_number):
    """Returns int, unix epoch timestamp of comment."""
    cdef unsigned int value
    MUD_getCommentTime(file_handle,comment_id_number,&value)
    return <int>value

def get_comment_author(file_handle,comment_id_number):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getCommentAuthor(file_handle,comment_id_number,title,256)
    return <object>(title.decode('cp1252'))

def get_comment_title(file_handle,comment_id_number):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getCommentTitle(file_handle,comment_id_number,title,256)
    return <object>(title.decode('cp1252'))
    
def get_comment_body(file_handle,comment_id_number):
    """Returns python string. Max number of characters: 8192."""
    cdef char title[8192]
    MUD_getCommentAuthor(file_handle,comment_id_number,title,8192)
    return <object>(title.decode('cp1252'))
        
### ======================================================================= ###
# HISTOGRAMS
### ======================================================================= ###
cdef extern from "../mud_src/mud_friendly.c":
    int MUD_getHists( int fh, unsigned int* pType, unsigned int* pNum )
    int MUD_getHistType( int fh, int num, unsigned int* pType )
    int MUD_getHistNumBytes( int fh, int num, unsigned int* pNumBytes )
    int MUD_getHistNumBins( int fh, int num, unsigned int* pNumBins )
    int MUD_getHistBytesPerBin( int fh, int num, unsigned int* pBytesPerBin )
    int MUD_getHistFsPerBin( int fh, int num, unsigned int* pFsPerBin )
    int MUD_getHistT0_Ps( int fh, int num, unsigned int* pT0_ps )
    int MUD_getHistT0_Bin( int fh, int num, unsigned int* pT0_bin )
    int MUD_getHistGoodBin1( int fh, int num, unsigned int* pGoodBin1 )
    int MUD_getHistGoodBin2( int fh, int num, unsigned int* pGoodBin2 )
    int MUD_getHistBkgd1( int fh, int num, unsigned int* pBkgd1 )
    int MUD_getHistBkgd2( int fh, int num, unsigned int* pBkgd2 )
    int MUD_getHistNumEvents( int fh, int num, unsigned int* pNumEvents )
    int MUD_getHistTitle( int fh, int num, char* title, int strdim )

    int MUD_getHistSecondsPerBin( int fh, int num, double* pSecondsPerBin )

    int MUD_getHistData( int fh, int num, void* pData )
    int MUD_getHistpData( int fh, int num, void** ppData )
        
def get_hists(file_handle):
    """Returns numpy array of int32: [data type, number of histograms]."""
    cdef unsigned int pType
    cdef unsigned int number_of_histograms
    MUD_getHists(file_handle,&pType,&number_of_histograms)
    return np.array([<int>pType,<int>number_of_histograms])
    
def get_hist_type(file_handle,hist_id_number):
    """Returns int, histogram data type, probably."""
    cdef unsigned int value
    MUD_getHistType(file_handle,hist_id_number,&value)
    return <int>value

def get_hist_n_bytes(file_handle,hist_id_number):
    """Returns int."""
    cdef unsigned int value
    MUD_getHistNumBytes(file_handle,hist_id_number,&value)
    return <int>value

def get_hist_n_bins(file_handle,hist_id_number):
    """Returns int. Number of bins in histogram."""
    cdef unsigned int value
    MUD_getHistNumBins(file_handle,hist_id_number,&value)
    return <int>value

def get_hist_bytes_per_bin(file_handle,hist_id_number):
    """Returns int."""
    cdef unsigned int value
    MUD_getHistBytesPerBin(file_handle,hist_id_number,&value)
    return <int>value

def get_hist_fs_per_bin(file_handle,hist_id_number):
    """Returns int."""
    cdef unsigned int value
    MUD_getHistFsPerBin(file_handle,hist_id_number,&value)
    return <int>value
    
def get_hist_t0_ps(file_handle,hist_id_number):
    """Returns int. Initial time of first bin, given in picoseconds."""
    cdef unsigned int value
    MUD_getHistT0_Ps(file_handle,hist_id_number,&value)
    return <int>value
    
def get_hist_t0_bin(file_handle,hist_id_number):
    """Returns int. Bin label of bin associated with time t0."""
    cdef unsigned int value
    MUD_getHistT0_Bin(file_handle,hist_id_number,&value)
    return <int>value

def get_hist_good_bin1(file_handle,hist_id_number):
    """Returns int."""
    cdef unsigned int value
    MUD_getHistGoodBin1(file_handle,hist_id_number,&value)
    return <int>value

def get_hist_good_bin2(file_handle,hist_id_number):
    """Returns int."""
    cdef unsigned int value
    MUD_getHistGoodBin2(file_handle,hist_id_number,&value)
    return <int>value
    
def get_hist_background1(file_handle,hist_id_number):
    """Returns int."""
    cdef unsigned int value
    MUD_getHistBkgd1(file_handle,hist_id_number,&value)
    return <int>value    

def get_hist_background2(file_handle,hist_id_number):
    """Returns int."""
    cdef unsigned int value
    MUD_getHistBkgd2(file_handle,hist_id_number,&value)
    return <int>value    

def get_hist_n_events(file_handle,hist_id_number):
    """Returns int."""
    cdef unsigned int value
    MUD_getHistNumEvents(file_handle,hist_id_number,&value)
    return <int>value    
    
def get_hist_title(file_handle,hist_id_number):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getHistTitle(file_handle,hist_id_number,title,256)
    return <object>(title.decode('cp1252'))
    
def get_hist_sec_per_bin(file_handle,hist_id_number):
    """Returns float."""
    cdef double value
    MUD_getHistSecondsPerBin(file_handle,hist_id_number,&value)
    return <float>value    

def get_hist_data(file_handle,hist_id_number):
    """Returns numpy array of ints: values contained in each histogram bin."""
    nbins = get_hist_n_bins(file_handle,hist_id_number)
    cdef array.array a = array.array('i',[0]*nbins)
    MUD_getHistData(file_handle,hist_id_number,&a.data.as_ints[0])
    cdef int[:] ca = a
    return np.array(ca)

def get_hist_data_pointer(file_handle,hist_id_number):
    print "Pointers not available in python. Please use get_hist_data."
    return 
    
### ======================================================================= ###
# SCALARS
### ======================================================================= ###
cdef extern from "../mud_src/mud_friendly.c":
    int MUD_getScalers( int fh, unsigned int* pType, unsigned int* pNum )
    int MUD_getScalerLabel( int fh, int num, char* label, int strdim )
    int MUD_getScalerCounts( int fh, int num, unsigned int* pCounts )
    
def get_scalers(file_handle):
    """Returns numpy array of int32: [data type, number of scalars]."""
    cdef unsigned int pType
    cdef unsigned int number_of_scalars
    MUD_getScalers(file_handle,&pType,&number_of_scalars)
    return np.array([<int>pType,<int>number_of_scalars])
    
def get_scaler_label(file_handle,scalar_id_number):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getScalerLabel(file_handle,scalar_id_number,title,256)
    return <object>(title.decode('Latin-1'))
    
def get_scaler_counts(file_handle,scalar_id_number):
    """Returns int."""
    cdef unsigned int value
    MUD_getScalerCounts(file_handle,scalar_id_number,&value)
    return <int>value
        
### ======================================================================= ###
# INDEPENDENT VARIABLES
### ======================================================================= ###
cdef extern from "../mud_src/mud_friendly.c":
    int MUD_getIndVars(int fh, unsigned int* pType, \
                       unsigned int* number_of_variables)
    int MUD_getIndVarLow( int fh, int num, double* pLow )
    int MUD_getIndVarHigh( int fh, int num, double* pHigh )
    int MUD_getIndVarMean( int fh, int num, double* pMean )
    int MUD_getIndVarStddev( int fh, int num, double* pStddev )
    int MUD_getIndVarSkewness( int fh, int num, double* pSkewness )
    int MUD_getIndVarName( int fh, int num, char* name, int strdim )
    int MUD_getIndVarDescription( int fh, int num, char* description,int strdim)
    int MUD_getIndVarUnits( int fh, int num, char* units, int strdim )
    
def get_ivars(file_handle):
    """Returns numpy array of int32: [data type, number of independent variables]."""
    cdef unsigned int pType
    cdef unsigned int number_of_variables
    MUD_getIndVars(file_handle,&pType,&number_of_variables)
    return np.array([<int>pType,<int>number_of_variables])
    
def get_ivar_low(file_handle,variable_id_number):
    """Returns float."""
    cdef double value
    MUD_getIndVarLow(file_handle,variable_id_number,&value)
    return <double>value

def get_ivar_high(file_handle,variable_id_number):
    """Returns float."""
    cdef double value
    MUD_getIndVarHigh(file_handle,variable_id_number,&value)
    return <double>value

def get_ivar_mean(file_handle,variable_id_number):
    """Returns float."""
    cdef double value
    MUD_getIndVarMean(file_handle,variable_id_number,&value)
    return <double>value
    
def get_ivar_std(file_handle,variable_id_number):
    """Returns float."""
    cdef double value
    MUD_getIndVarStddev(file_handle,variable_id_number,&value)
    return <double>value  
    
def get_ivar_skewness(file_handle,variable_id_number):
    """Returns float."""
    cdef double value
    MUD_getIndVarSkewness(file_handle,variable_id_number,&value)
    return <double>value

def get_ivar_name(file_handle,variable_id_number):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getIndVarName(file_handle,variable_id_number,title,256)
    return <object>(title.decode('cp1252'))

def get_ivar_description(file_handle,variable_id_number):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getIndVarDescription(file_handle,variable_id_number,title,256)
    return <object>(title.decode('cp1252')) 
    
def get_ivar_units(file_handle,variable_id_number):
    """Returns python string. Max number of characters: 256."""
    cdef char title[256]
    MUD_getIndVarUnits(file_handle,variable_id_number,title,256)
    return <object>(title.decode('cp1252'))
