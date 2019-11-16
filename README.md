# Package Overview

Beta-data package.

## Setup 

* Install using pip: `pip install bdata`
* OPTIONAL: Export the following environment variables to set the local data storage location (add to `.bashrc`):
   Set `BNMR_ARCHIVE` and `BNQR_ARCHIVE` the following scheme points to the msr files:
   ```bash
      ${BNMR_ARCHIVE}/year/filename.msr
      ${BNQR_ARCHIVE}/year/filename.msr
   ```
   By default `bdata` will look for data in `$HOME/.bdata/`. If the requested run is not found locally, an attempt to downlaod the file from [musr.ca](http://musr.ca/mud/runSel.html) will ensue. The file will be written to disk at the appropriate location. 

## Contents

* [`mdata`](#mdata) [object]: access general MUD files, provides special containers
* [`bdata`](#bdata) [object]: access BNMR MUD files
* [`bjoined`](#bjoined) [object]: combine `bdata` objects
* [`life`](#life) [`mdict` object]: dictionary of probe lifetimes. 
* [`mudpy`](#mudpy) [C wrapper]: python access to MUD C functions

# [mdata](https://github.com/dfujim/bdata/blob/master/bdata/mdata.py)
mud-data object. The mdata object is a data container designed for easy reading of any MUD file, regardless of experiment type or mesurement method. 

## Object Map

**Signature**: 

`mdata(filename)`

Example: `mud = mdata('filename.msr')`


## Misc Features

### Representation

   Representation has been nicely formatted so that typing the object 
   name into the interpreter produces nice output. 

### Operators

   mvar, mscaler, and mhist objects allow for arithmatic or logic 
   operators to be used, where the value used in the operation is the 
   mean, count, or data array respectively. 

   Example:    `mud.ivar['BNMR:HVBIAS:POS:RDVOL'] + 1`
   is equivalent to 
               `mud.ivar['BNMR:HVBIAS:POS:RDVOL'].mean + 1`

### Special Rules For Attributes

   If an attribute is not found in mdata, it will look for the 
   attribute in the bdict objects in the order: hist, ivar.
   This second-level attribute search is much slower than regular 
   access.

   mdict objects all allow assignment and fetching of dictionary keys 
   as if they were attributes. Note that one can replace `+` with `p`,
   and `-` with `m` to allow fetching of histograms. 

   Example: `mud.hist.Bp`, `mud.hist['B+']`, `mud.Bp` all have the 
            exact same output, with the last being much slower than 
            the others.

# [bdata](https://github.com/dfujim/bdata/blob/master/bdata/bdata.py)
Beta-data object, inherits from [`mdata`](#mdata). The bdata object is a data container with some basic analysis capabilities, designed to read out [MUD](http://musr.ca/mud/mud_fmt.html) data files and to provide user-friendly access to the file headers and provide asymmetry calculations. 

## Object Map

**Signature**: 

`bdata(run_number,year=None,filename='')`

Examples:
    
```python
b = bdata(40001)                     # read run 40001 from the current year. 
b = bdata(40001,year=2017)           # read run 40001 from year 2017.
b = bdata(0,filename='filename.msr') # read file from local memory, run number unused 
```        

**Functions**: 

| Signature | Description |
| -------- | -------- |
| [`asym(option="",omit="",rebin=1,hist_select='',nbm=False)`](https://github.com/dfujim/bdata/blob/64495ec255cd4a0a6aee6f8f8b97607adef73e88/bdata/bdata.py#L903)     | Calculate asymmetry. |
| [`beam_kev(get_error=False)`](https://github.com/dfujim/bdata/blob/64495ec255cd4a0a6aee6f8f8b97607adef73e88/bdata/bdata.py#L1316)     | Get beam implantation energy in keV     |
| [`get_pulse_s()`](https://github.com/dfujim/bdata/blob/64495ec255cd4a0a6aee6f8f8b97607adef73e88/bdata/bdata.py#L1353)     | Get beam pulse duration in s     |

## Misc Features

In addition to those provided by [`mdata`](#mdata).

### Special Rules For Attributes

   If an attribute is not found in bdata, it will look for the 
   attribute in the mdict objects in the order: camp, epics, ppg, hist.
   This second-level attribute search is much slower than regular 
   access.



# [bjoined](https://github.com/dfujim/bdata/blob/master/bdata/bjoined.py)

Object for combining bdata objects. Attribute access works through lists (see examples below). Histogram counts are summed over to emulate data taken within a single run. bdata asymmetry calculations operate on these summed histograms. Additional functionality for proper weighted  means of asymmetries of the invididual runs is also given.

## Object Map

**Signature**: 

`bjoined(bdata_list)`

Examples:
    
```python
blist = [bdata(r,year=2019) for r in range(40010,40013)] # read runs 40010-40012
bjnd = bjoined(blist)                                    # combine these runs
```        

**Functions**: 

In addtion to the [`bdata`](#bdata) functions, `bjoined` also provides:

| Signature | Description |
| -------- | -------- |
| [`asym_mean(*asym_args,**asym_kwargs)`](https://github.com/dfujim/bdata/blob/64495ec255cd4a0a6aee6f8f8b97607adef73e88/bdata/bjoined.py#L237)     | Take weighted mean of individual asymmetries. Arguments are passed to `bdata.asym()`   |


## Misc Features

### Special Rules For Attributes and Lists

   Attribute access passes through list objects. For example, if we have created the `bjnd` object from the previous example, we run 
   
   ```python
   bjnd.camp
   ```
   
   we get a list of `mdict` objects. We can access the magnetic field strength as follows: 
   
   ```python
   bjnd.camp.b_field
   ```
  
   or a list of the mean values:
   
   ```python
   bjnd.camp.b_field.mean
   ```
   
   despite the fact that at each stage a list is returned. Attribute lookup is treated the same as in [`bdata`](#bdata) so that the above could be shortened to 
  
  ```python
   bjnd.b_field.mean
   ```
   
   with some small penalty to run time.
   
# [life](https://github.com/dfujim/bdata/blob/481ab42cdd39a86266431176a3853e354ea385aa/bdata/bdata.py#L1663-L1682)

Probe lifetimes. Example:

```python
import bdata as bd
lifeitme = bd.life.Li8
error = bd.life.Li8_err
```

Probes implemented are keyed by `Li8`, `Li9`, `Be11`, `F20`, `Mg31`, `Ac230`, `Ac234`.

# [mudpy](https://github.com/dfujim/bdata/blob/master/bdata/mudpy.pyx)

Wrap the [mud_friendly.c](http://musr.ca/mud/mud_friendly.html) functions using Cython. Gives low-level access to mud files.

**Functions**: 

File IO

|Cython Function (python-accessible) |C Function (wrapped) |
| -------- | -------- |
|`open_read(file_name)` |`int MUD_openRead(char* file_name, unsigned int* pType)` |
|`close_read(file_handle)` |`void MUD_closeRead(int file_handle)` |

Headers

|Cython Function (python-accessible) |C Function (wrapped) |
| -------- | -------- |
|`get_description(file_handle)` |`int MUD_getRunDesc(int fh, unsigned int* pType)` |
|`get_exp_number(file_handle)` |`int MUD_getExptNumber(int fh, unsigned int* pExpNumber)` |
|`get_run_number(file_handle)` |`int MUD_getRunNumber(int fh, unsigned int* pRunNumber)` |
|`get_elapsed_seconds(file_handle)` |`int MUD_getElapsedSec(int fh, unsigned int* pElapsedSec)` |
|`get_start_time(file_handle)` |`int MUD_getTimeBegin(int fh, unsigned int* pTimeBegin)` |
|`get_end_time(file_handle)` |`int MUD_getTimeEnd(int fh, unsigned int* pTimeEnd)` |
|`get_title(file_handle)` |`int MUD_getTitle(int fh, char* string, int strdim)` |
|`get_lab(file_handle)` |`int MUD_getLab(int fh, char* string, int strdim)` |
|`get_area(file_handle)` |`int MUD_getArea(int fh, char* string, int strdim)` |
|`get_method(file_handle)` |`int MUD_getMethod(int fh, char* string, int strdim)` |
|`get_apparatus(file_handle)` |`int MUD_getApparatus(int fh, char* string, int strdim)` |
|`get_insert(file_handle)` |`int MUD_getInsert(int fh, char* string, int strdim)` |
|`get_sample(file_handle)` |`int MUD_getSample(int fh, char* string, int strdim)` |
|`get_orientation(file_handle)` |`int MUD_getOrient(int fh, char* string, int strdim)` |
|`get_das(file_handle)` |`int MUD_getDas(int fh, char* string, int strdim)` |
|`get_experimenter(file_handle)` |`int MUD_getExperimenter(int fh, char* string, int strdim)` |
|`get_temperature(file_handle)` |`int MUD_getTemperature(int fh, char* string, int strdim )` |
|`get_field(file_handle)` |`int MUD_getField(int fh, char* string, int strdim )` |

Comments

|Cython Function (python-accessible) |C Function (wrapped) |
| -------- | -------- |
|`get_comments(file_handle)` |`int MUD_getComments(int fh, unsigned int* pType, unsigned int* number_of_comments)` |
|`get_comment_prev(file_handle,comment_id_number)` |`int MUD_getCommentPrev(int fh, int num, unsigned int* pPrev )` |
|`get_comment_next(file_handle,comment_id_number)` |`int MUD_getCommentNext(int fh, int num, unsigned int* pNext )` |
|`get_comment_time(file_handle,comment_id_number)` |`int MUD_getCommentTime(int fh, int num, unsigned int* pTime )` |
|`get_comment_author(file_handle,comment_id_number)` |`int MUD_getCommentAuthor(int fh, int num, char* author, int strdim )` |
|`get_comment_title(file_handle,comment_id_number)` |`int MUD_getCommentTitle(int fh, int num, char* title, int strdim )` |
|`get_comment_body(file_handle,comment_id_number)` |`int MUD_getCommentBody(int fh, int num, char* body, int strdim )` |

Histograms

|Cython Function (python-accessible) |C Function (wrapped) |
| -------- | -------- |
|`get_hists(file_handle)` |`int MUD_getHists( int fh, unsigned int* pType, unsigned int* pNum )` |
|`get_hist_type(file_handle,hist_id_number)` |`int MUD_getHistType( int fh, int num, unsigned int* pType )` |
|`get_hist_n_bytes(file_handle,hist_id_number)` |`int MUD_getHistNumBytes( int fh, int num, unsigned int* pNumBytes )` |
|`get_hist_n_bins(file_handle,hist_id_number)` |`int MUD_getHistNumBins( int fh, int num, unsigned int* pNumBins )` |
|`get_hist_bytes_per_bin(file_handle,hist_id_number)` |`int MUD_getHistBytesPerBin( int fh, int num, unsigned int* pBytesPerBin )` |
|`get_hist_fs_per_bin(file_handle,hist_id_number)` |`int MUD_getHistFsPerBin( int fh, int num, unsigned int* pFsPerBin )` |
|`get_hist_t0_ps(file_handle,hist_id_number)` |`int MUD_getHistT0_Ps( int fh, int num, unsigned int* pT0_ps )` |
|`get_hist_t0_bin(file_handle,hist_id_number)` |`int MUD_getHistT0_Bin( int fh, int num, unsigned int* pT0_bin )` |
|`get_hist_good_bin1(file_handle,hist_id_number)` |`int MUD_getHistGoodBin1( int fh, int num, unsigned int* pGoodBin1 )` |
|`get_hist_good_bin2(file_handle,hist_id_number)` |`int MUD_getHistGoodBin2( int fh, int num, unsigned int* pGoodBin2 )` |
|`get_hist_background1(file_handle,hist_id_number)` |`int MUD_getHistBkgd1( int fh, int num, unsigned int* pBkgd1 )` |
|`get_hist_background2(file_handle,hist_id_number)` |`int MUD_getHistBkgd2( int fh, int num, unsigned int* pBkgd2 )` |
|`get_hist_n_events(file_handle,hist_id_number)` |`int MUD_getHistNumEvents( int fh, int num, unsigned int* pNumEvents )` |
|`get_hist_title(file_handle,hist_id_number)` |`int MUD_getHistTitle( int fh, int num, char* title, int strdim )` |
|`get_hist_sec_per_bin(file_handle,hist_id_number)` |`int MUD_getHistSecondsPerBin( int fh, int num, double* pSecondsPerBin )` |
|`get_hist_data(file_handle,hist_id_number)` |`int MUD_getHistData( int fh, int num, void* pData )` |
|`get_hist_data_pointer(file_handle,hist_id_number)` |`int MUD_getHistpData( int fh, int num, void** ppData )` |

Scalers

|Cython Function (python-accessible) |C Function (wrapped) |
| -------- | -------- |
|`get_scalers(file_handle)` |`int MUD_getScalers( int fh, unsigned int* pType, unsigned int* pNum )` |
|`get_scaler_label(file_handle,scalar_id_number)` |`int MUD_getScalerLabel( int fh, int num, char* label, int strdim )` |
|`get_scaler_counts(file_handle,scalar_id_number)` |`int MUD_getScalerCounts( int fh, int num, unsigned int* pCounts )` |

Independent Variables

|Cython Function (python-accessible) |C Function (wrapped) |
| -------- | -------- |
|`get_ivars(file_handle)` |`int MUD_getIndVars(int fh, unsigned int* pType, unsigned int* number_of_variables)` |
|`get_ivar_low(file_handle,variable_id_number)` |`int MUD_getIndVarLow( int fh, int num, double* pLow )` |
|`get_ivar_high(file_handle,variable_id_number)` |`int MUD_getIndVarHigh( int fh, int num, double* pHigh )` |
|`get_ivar_mean(file_handle,variable_id_number)` |`int MUD_getIndVarMean( int fh, int num, double* pMean )` |
|`get_ivar_std(file_handle,variable_id_number)` |`int MUD_getIndVarStddev( int fh, int num, double* pStddev )` |
|`get_ivar_skewness(file_handle,variable_id_number)` |`int MUD_getIndVarSkewness( int fh, int num, double* pSkewness )` |
|`get_ivar_name(file_handle,variable_id_number)` |`int MUD_getIndVarName( int fh, int num, char* name, int strdim )` |
|`get_ivar_description(file_handle,variable_id_number)` |`int MUD_getIndVarDescription( int fh, int num, char* description,int strdim)` |
|`get_ivar_units(file_handle,variable_id_number)` |`int MUD_getIndVarUnits( int fh, int num, char* units, int strdim )` |
