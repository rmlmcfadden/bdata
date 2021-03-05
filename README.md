# bdata 

<a href="https://pypi.org/project/bdata/" alt="PyPI Version"><img src="https://img.shields.io/pypi/v/bdata?label=PyPI%20Version"/></a>
<img src="https://img.shields.io/pypi/format/bdata?label=PyPI%20Format"/>
<img src="https://img.shields.io/github/languages/code-size/dfujim/bdata"/>
<img src="https://img.shields.io/tokei/lines/github/dfujim/bdata"/>
<img src="https://img.shields.io/pypi/l/bdata"/>

<a href="https://github.com/dfujim/bdata/commits/master" alt="Commits"><img src="https://img.shields.io/github/commits-since/dfujim/bdata/latest/master"/></a>
<a href="https://github.com/dfujim/bdata/commits/master" alt="Commits"><img src="https://img.shields.io/github/last-commit/dfujim/bdata"/></a>

[bdata] is a lightwieght [Python] package aimed to aid in the analysis of β-detected
nuclear magnetic/quadrupole resonance (β-NMR and β-NQR) data taken at [TRIUMF]. 
These techniques are similar to muon spin rotation ([μSR]) and "conventional"
nuclear magnetic resonance ([NMR]), but use radioactive nuclei as their [NMR]
probe in place of the [muon] or a stable isotope.

The intended user of [bdata] is anyone analyzing data taken from [TRIUMF]'s β-NMR or β-NQR spectrometers.
A key goal of the project is to alleviate much of the technical tedium that is
often encountered during any analysis.

Used with [bfit] and the [SciPy] ecosystem, [bdata] forms part of a flexible API
in the analysis of β-NMR and β-NQR data. [bdata] has been written to fullfill the following needs: 

* Provide an intuitive means of interfacing with [MUD] files in [Python].
* Fetch missing local data from the [archive]. 
* Support analyses by providing common data manipulations, such as calculting 
asymmetries or combining scans. 

## Citing

If you use [mudpy], [bdata], or [bfit] in your work, please cite:

- D. Fujimoto.
  <i>Digging into MUD with Python: mudpy, bdata, and bfit</i>.
  <a href="https://arxiv.org/abs/2004.10395">
  arXiv:2004.10395 [physics.data-an]</a>.

## Community Guidelines

* Please submit contributions to [bdata] via a pull request
* To report issues or get support, please file a new issue

## Installation and Use

### Dependencies

The following packages/applications are needed prior to [bfit] installation:
- [Python] 3.6 or higher: a dynamically typed programming language. [[install](https://wiki.python.org/moin/BeginnersGuide/Download)]
- [Cython] : [C]-language extensions for [Python]. [[install](https://cython.readthedocs.io/en/latest/src/quickstart/install.html)]
- [NumPy] : array programming library for [Python]. [[install](https://numpy.org/install/)]


and the following are handelled automatically when retrieving [bfit] from the [PyPI]:

- [iminuit] : a [Jupyter]-friendly [Python] interface for the [MINUIT2] library.
- [mudpy] : data structures for parsing [TRIUMF] [MUD] files.
- [pandas] : a fast, powerful, flexible and easy to use data analysis/manipulation tool.
- [requests] : an elegant and simple [HTTP] library for [Python].


### Install Instructions

|  | Command |
|:-- | :--|
From the [PyPI] as user (recommended) | `pip install --user bdata` |
From the [PyPI] as root | `pip install bdata` |
From source | `python3 setup.py install` |

Note that `pip` should point to a (version 3) [Python] executable
(e.g., `python3`, `python3.8`, etc.).
If the above does not work, try using `pip3` or `python3 -m pip` instead.

### Optional Configuration

For convenience,
you may want to tell [bdata] where the data is stored on your machine.
This is done by defining two environment variables:
`BNMR_ARCHIVE` and `BNQR_ARCHIVE`.
This can be done, for example, in your `.bashrc` script.
Both variables expect the data to be stored in directories with a particular
heirarchy:

```
/path/
    bnmr/
    bnqr/
        2017/
        2018/
            045123.msr
```

Here, the folders `/path/bnmr/` and `/path/bnqr/` both contain runs
(i.e., `.msr` files) organized into subdirectories by year of aquasition.
In this case, you would set (in your `.bashrc`):

```bash
export BNMR_ARCHIVE=/path/bnmr/
export BNQR_ARCHIVE=/path/bnqr/
```

If [bdata] cannot find the data, it will attempt to download the relavent [MUD] files 
from the [archive] and store them in `$HOME/.bdata`.
This is the default behaviour for [bdata] installed from [PyPI].

## Contents

* [`bdata`](#bdata) [object]: access β-NMR and β-NQR [MUD] files
* [`bjoined`](#bjoined) [object]: append `bdata` objects
* [`bmerged`](#bmerged) [object]: combine `bdata` objects
* [`life`](#life) [`mdict` object]: dictionary of probe lifetimes. 

# [bdata](https://github.com/dfujim/bdata/blob/master/bdata/bdata.py)
Beta-data object, inherits from [`mdata`](#mdata). The bdata object is a data container with some basic analysis capabilities, designed to read out [MUD] data files and to provide user-friendly access to the file headers and provide asymmetry calculations. 

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
| [`asym(option="", omit="", rebin=1, hist_select='', nbm=False, deadtime=0)`](https://github.com/dfujim/bdata/blob/c5ec55c82b2380c538fbf615722bf08d8f4116c6/bdata/bdata.py#L1116-L1298) | Calculate asymmetry. |
| [`beam_kev(get_error=False)`](https://github.com/dfujim/bdata/blob/c5ec55c82b2380c538fbf615722bf08d8f4116c6/bdata/bdata.py#L1634-L1640) | Get beam implantation energy in keV |
| [`get_deadtime(self, dt=1e-9, c=1, return_minuit=False, fixed='c')`](https://github.com/dfujim/bdata/blob/3197c29ab5a9a0290fa0ecee50cd5fe0c8ae538e/bdata/bdata.py#L1655-L1673) | Get deadtime estimate in s, scaling factor, or chi2 |
| [`get_pulse_s()`](https://github.com/dfujim/bdata/blob/c5ec55c82b2380c538fbf615722bf08d8f4116c6/bdata/bdata.py#L1724-L1725) | Get beam pulse duration in s |

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

[Python]: https://www.python.org/
[SciPy]: https://www.scipy.org/
[Cython]: https://cython.org/
[NumPy]: https://numpy.org/
[pandas]: https://pandas.pydata.org/
[Matplotlib]: https://matplotlib.org/
[requests]: https://requests.readthedocs.io/en/master/
[Jupyter]: https://jupyter.org/

[YAML]: https://yaml.org/
[C]: https://en.wikipedia.org/wiki/C_(programming_language)
[HTTP]: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol

[TRIUMF]: https://www.triumf.ca/
[CMMS]: https://cmms.triumf.ca
[MUD]: https://cmms.triumf.ca/mud/
[archive]: https://cmms.triumf.ca/mud/runSel.html

[UBC]: https://www.ubc.ca/
[μSR]: https://en.wikipedia.org/wiki/Muon_spin_spectroscopy
[NMR]: https://en.wikipedia.org/wiki/Nuclear_magnetic_resonance
[muon]: https://en.wikipedia.org/wiki/Muon

[PyPI]: https://pypi.org/project/bdata/
[mudpy]: https://github.com/dfujim/mudpy
[bdata]: https://github.com/dfujim/bdata
[bfit]: https://github.com/dfujim/bfit

[iminuit]: https://github.com/scikit-hep/iminuit
[MINUIT2]: https://root.cern/doc/master/Minuit2Page.html
