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

* [`bdata`](#bdata) [object]: access BNMR MUD files
* [`bjoined`](#bjoined) [object]: combine `bdata` objects
* [`life`](#life) [`bdict` object]: dictionary of probe lifetimes. 

# [bdata](https://github.com/dfujim/bdata/blob/master/bdata/bdata.py)
Beta-data object. The bdata object is a data container with some basic analysis capabilities, designed to read out [MUD](http://musr.ca/mud/mud_fmt.html) data files and to provide user-friendly access to the file headers and provide asymmetry calculations. 

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
| `asym(option="",omit="",rebin=1,hist_select='',nbm=False)`     | Calculate asymmetry. See [docstring](https://github.com/dfujim/bdata/blob/481ab42cdd39a86266431176a3853e354ea385aa/bdata/bdata.py#L996-L1158).     |
| `beam_kev()`     | Get beam implantation energy in keV     |
| `get_pulse_s()`     | Get beam pulse duration in s     |


## Misc Features

### Representation

   Representation has been nicely formatted so that typing the object 
   name into the interpreter produces nice output. 

### Operators

   bvar, bscaler, and bhist objects allow for arithmatic or logic 
   operators to be used, where the value used in the operation is the 
   mean, count, or data array respectively. 

   Example:    `b.ppg.bias15 + 1`
   is equivalent to 
               `b.ppg.bias15.mean + 1`

### Special Rules For Attributes

   If an attribute is not found in bdata, it will look for the 
   attribute in the bdict objects in the order: camp, epics, ppg, hist.
   This second-level attribute search is much slower than regular 
   access.

   bdict objects all allow assignment and fetching of dictionary keys 
   as if they were attributes. Note that one can replace `+` with `p`,
   and `-` with `m` to allow fetching of histograms. 

   Example: `b.ppg.beam_on`, `b.ppg['beam_on']`, `b.beam_on` all have the 
            exact same output, with the last being much slower than 
            the others.

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
| `asym_mean(self,*asym_args,**asym_kwargs)`     | Take weighted mean of individual asymmetries. Arguments are passed to `bdata.asym()`   |


## Misc Features

### Special Rules For Attributes and Lists

   Attribute access passes through list objects. For example, if we have created the `bjnd` object from the previous example, we run 
   
   ```python
   bjnd.camp
   ```
   
   we get a list of `bdict` objects. We can access the magnetic field strength as follows: 
   
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

Access is given through the following example:

```python
import bdata as bd
bd.life.Li8
```
