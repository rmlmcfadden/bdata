# Package Overview

Beta-data package.

## Setup 

### Dependencies needed pre-install: 

* python development version: `sudo apt-get install python3-dev` (on Ubuntu, for example)

### Install 

* Install using pip: `pip3 install bdata`

### Optional Configuration

* For bdata: Export the following environment variables to set the local data storage location (add to `.bashrc`):
   Set `BNMR_ARCHIVE` and `BNQR_ARCHIVE` the following scheme points to the msr files:
   ```bash
      ${BNMR_ARCHIVE}/year/filename.msr
      ${BNQR_ARCHIVE}/year/filename.msr
   ```
   By default `bdata` will look for data in `$HOME/.bdata/`. If the requested run is not found locally, an attempt to downlaod the file from [musr.ca](http://musr.ca/mud/runSel.html) will ensue. The file will be written to disk at the appropriate location. 

## Contents

* [`bdata`](#bdata) [object]: access BNMR MUD files
* [`bjoined`](#bjoined) [object]: append `bdata` objects
* [`bmerged`](#bmerged) [object]: combine `bdata` objects
* [`life`](#life) [`mdict` object]: dictionary of probe lifetimes. 

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

Object for appending bdata objects. Attribute access works through lists (see examples below). Histogram counts are summed over to emulate data taken within a single run. bdata asymmetry calculations operate on these summed histograms. Additional functionality for proper weighted  means of asymmetries of the invididual runs is also given.

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
   
# [bmerged](https://github.com/dfujim/bdata/blob/master/bdata/bmerged.py)

Object for combining bdata objects. Unlike [`bjoined`](#bjoined), `bmerged` should look and behave more or less identically to the [`bdata`](#bdata) object. In this way, runs can be combined and replaced in existing code with little modification. Histograms are combined in the same was as [`bjoined`](#bjoined): counts are summed over to emulate data taken within a single run. [`bdata`](#bdata) asymmetry calculations operate on these summed histograms. 

## Object Map

**Signature**: 

`bmerged(bdata_list)`

Examples:
    
```python
blist = [bdata(r,year=2019) for r in range(40010,40013)] # read runs 40010-40012
bjnd = bmerged(blist)                                    # combine these runs
```
   
# [life](https://github.com/dfujim/bdata/blob/481ab42cdd39a86266431176a3853e354ea385aa/bdata/bdata.py#L1663-L1682)

Probe lifetimes. Example:

```python
import bdata as bd
lifeitme = bd.life.Li8
error = bd.life.Li8_err
```

Probes implemented are keyed by `Li8`, `Li9`, `Be11`, `F20`, `Mg31`, `Ac230`, `Ac234`.
