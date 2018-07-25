# bdata
Contains both bdata and mudpy python modules.


Beta-data package. The bdata object is largely a data container, designed to read out [MUD](http://musr.ca/mud/mud_fmt.html) data files and to provide user-friendly access [BNMR/BNQR data](http://musr.ca/mud/runSel.html). Data files are read either from a directory specified by environment variable (see installation notes), or from a passed filename for easy external user access. The [MUD](http://musr.ca/mud/mud_fmt.html) data file is read and closed on object construction. 

This package also provides direct python access to the [MUD](http://musr.ca/mud/mud_fmt.html) file format in the `bdata.mudpy` module. 

Constructor: `bdata(run_number,year=0,filename='')`
    
```python
bd = bdata(40001)                     # read run 40001 from the default year. 
bd = bdata(40001,year=2009)           # read run 40001 from year 2009.
bd = bdata(0,filename='filename.msr') # read file from local memory, run number unused 
```        

If `year=0` then default is the current year. For scripts analysing a specific data set, it is advised that this be set so that the script does not break as time passes. 

## Installation 

* Install using pip: `pip install bdata`
* Export environment variables for finding data files (add to `.bashrc` or similar)
    * `export BNMR_ARCHIVE=/path/bnmr/`
    * `export BNQR_ARCHIVE=/path/bnqr/`

## Example Usage

1 Asymmetry: 

```python
bd.asym() # for details and options see bdata.asym docstring. 
```        

2 Beam energy: 

```python
bd.beam_kev()   # returns beam energy in keV
```

3 Pulse-off time for SLR measurements: 

```python
pulse_off_s()
```                             

4 For a nicely-formatted list of all data fields call the fields method: 

```python
bd.fields()
```
        
Note that the object representation has been nicely formatted as well, so that typing
   
```python
bd
```
        
into the interpreter produces nice output. 


## Notes

The bdict objects allow for the calling of dictionary keys like an object attribute. For example, bd.ppg.beam_on or bd.ppg['beam_on'] have the exact same output. Note that reserved characters such as '+' cannot be used in this manner. 
            
Set the location of the data archive via environment variables "BNMR_ARCHIVE" and "BNQR_ARCHIVE". This would be something like "/data1/bnmr/dlog/" on linbnmr2 or "~/triumf/data/bnmr/" on muesli or lincmms.

## bdata.asym() docstring

```text
Calculate and return the asymmetry for various run types. 

usage: asym(option="",omit="",rebin=1,hist_select='')

Inputs:
    options:        see below for details
    omit:           1f bins to omit if space seperated string in options is not feasible. See options description below.
    rebin:          SLR only. Weighted average over 'rebin' bins to reduce array length by a factor of rebin. 
    hist_select:    string to specify which histograms get combined into making the asymmetry calculation. 
                        Deliminate with [,] or [;]. Histogram names cannot therefore contain either of these characters.

Asymmetry calculation outline (with default detectors): 

    Split helicity      (NMR): (F-B)/(F+B) for each
    Combined helicity   (NMR): (r-1)/(r+1) where r = sqrt([(B+)(F-)]/[(F+)(B-)])

    Split helicity      (NQR): (R-L)/(R+L) for each
    Combined helicity   (NQR): (r-1)/(r+1) where r = sqrt([(L+)(R-)]/[(R+)(L-)])

Histogram Selection 

    If we wished to do a simple asymmetry calculation in the form of 

                            (F-B)/(F+B)

    for each helicity, then 
                                |--|  |--|   paired helicities
                hist_select = 'F+,B+,F-,B-'
                               |-----|       paired counter location
                                  |-----|
Status of Data Corrections:
    SLR: 
        Removes prebeam bins. 
        Subtract mean of prebeam bins from raw counts (does not treat error propagation from this. Errors are still treated 
            as Poisson, despite not being integers) 

        Rebinning: 
            returned time is average time over rebin range
            returned asym is weighted mean

    1F: 
        Allows manual removal of unwanted bins. 

        Scan Combination:
            Multiscans are considered as a single scan with long integration time. Histogram bins are summed according to 
                their frequency bin, errors are Poisson.

    1N:
        Same as 1F. Uses the neutral beam monitor values to calculate 
        asymetries in the same manner as the NMR calculation. 

    2E: 
        Prebeam bin removal. 
        Postbeam bin removal. Assumes beamoff time is 0. 
        Splits saved 1D histograms into 2D.

        Asymmetry calculations: 
            raw: calculated through differences method (as described in the asymmetry calculation outline)
            dif: let 0 be the index of the centermost scan in time. dif asymmetries are then calculated via raw[i+1]-raw[i-1], 
                where "raw" is as calculated in the above line, for each 
                of the three types: +,-,combined 
            sl: take a weighted least squares fit to the two bins prior and the two bins after the center bin (in time). For 
                each find the value of the asymmetry at the center time position. Take the difference: post-prior

Return value depends on option provided:

    SLR DESCRIPTIONS --------------------------------------------------

    "":     dictionary of 2D numpy arrays keyed by {"p","n","c","time_s"} for each helicity and combination (val,err). 
                Default return state for unrecognized options
    "h":    dictionary 2D numpy arrays keyed by {"p","n","time_s"} for each helicity (val,err).
    "p":    2D np array of up helicity state [time_s,val,err].
    "n":    2D np array of down helicity state [time_s,val,err].
    "c":    2D np array of combined asymmetry [time_s,val,err].

    1F DESCRIPTIONS ---------------------------------------------------

        all options can include a space deliminated list of bins or ranges of bins which will be omitted. ex: "raw 1 2 5-20 3"

    "":     dictionary of 2D numpy arrays keyed by {p,n,c,freq} for each helicity and combination [val,err]. Default return state 
                for unrecognized options.
    "r":    Dictionary of 2D numpy arrays keyed by {p,n} for each helicity (val,err), but listed by bin, not combined by 
                frequency. 
    "h":    get unshifted +/- helicity scan-combined asymmetries as a dictionary {'p':(val,err),'n':(val,err),'freq'}
    "p":    get pos helicity states as tuple, combined by frequency (freq,val,err)
    "n":    similar to p but for negative helicity states
    "c":    get combined helicity states as tuple (freq,val,err)


    2E DESCRIPTIONS ---------------------------------------------------

        Takes no options. Returns a dictionary with the keys: 

    'dif_p':    [val,err][frequency] of pos. helicity asymmetry 
    'dif_n':    [ve][f] of negative helicity asymmetry
    'dif_c':    [ve][f] of combined helicity asymmetry

    'raw_p':    [ve][f][time] raw asymmetries of each time bin. Pos hel. 
    'raw_n':    [ve][f][t] negative helicity.
    'raw_c':    [ve][f][t] combined helicity

    'freq':     [f] frequency values
    'time':     [t] time bin values

    'sl_p':     [ve][f] pos. hel. of asymmetry calcuated through slopes of pre and post middle time bin. Slope method only 
                    for >= 5 time bins, corresponds to >= 3 RF on delays
    'sl_n':     [ve][f] negative helicity.
    'sl_c':     [ve][f] combined helicity.
```        
