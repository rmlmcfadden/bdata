# Python object for combining bdata objects, resulting in an object that 
# behaves exactly like a bdata object. 
# Derek Fujimoto 
# Mar 2020

from bdata import bdata
from bdata.mdata import mdict,mhist,mlist,mvar
import numpy as np
import pandas as pd
import re

class bmerged(bdata):
    """
        Object to store lists or the combination of bdata objects, emulates
        bdata object on completion
    """


    # ======================================================================= #
    def __init__(self,bdata_list):
        """
            bdata_list:               list of bdata objects
        """
        
        # sort by run number
        runs = [b.run for b in bdata_list]
        idx = np.argsort(runs)
        bdata_list = np.array(bdata_list)[idx]
        runs = np.array(runs)[idx]
        years = np.array([b.year for b in bdata_list])
        
        # set some common parameters
        for key in ('apparatus','area','das','description','duration','end_date',
                    'end_time','exp','experimenter','lab','method','mode',
                    'orientation','sample','start_date','start_time','title'):
                        
            x = np.array([getattr(b,key) for b in bdata_list])
            setattr(self,key,self._combine_values(key,x))
            
        # set the run number and year
        self.run = int(''.join(map(str,runs)))
        self.year = int(''.join(map(str,years)))
        
        # set ppg, camp, and epics
        for top in ('ppg','epics','camp'):
            
            d = mdict()
            
            keys = list(getattr(bdata_list[0],top).keys())
            x = mlist([getattr(b,top) for b in bdata_list])
            for key in keys:
                var = mvar()    
                for attr in var.__slots__:
                    setattr(var,attr,self._combine_values(attr,getattr(x[key],attr)))
                d[key] = var
            setattr(self,top,d)
            
        # combine the histograms
        self._combine_hist(bdata_list)
    
    # ======================================================================= #
    def _combine_hist(self,bdata_list):
        """
            Apply np.sum to base histograms and set result to top level
            
            Scans are concatenated. 
            SLR histograms are summed.
        """
        
        hist = mlist([b.hist for b in bdata_list])
        
        # these will get combined
        hist_names = ('F+','F-','B+','B-',
                      'L+','L-','R+','R-',
                      'NBMF+','NBMF-','NBMB+','NBMB-')
        
        # these modes require appending scans rather than averaging
        hist_xnames = ('Frequency','x parameter',)
        
        # make container
        hist_joined = mdict()
        
        # check if x values in histogram
        do_append = any([h in hist[0] for h in hist_xnames])
        
        # get x histogram name
        if do_append:
            for xname in hist_xnames: 
                if xname in hist[0]: 
                    break
            
        for name in hist[0].keys():
            
            # no rule for combining histogram
            if (name not in hist_names) and (name not in hist_xnames): continue
            
            # make the object                            
            hist_obj = mhist()
                        
            # combine scan-less runs (just add the histogrms)
            if not do_append:
                hist_data = np.sum(list(hist[name].data),axis=0)
            
            # combine runs with scans (append the data)
            elif name in hist_xnames:                
                hist_obj.data = np.concatenate(hist[xname].data)
            else:
                hist_obj.data = np.concatenate(hist[name].data)    
            
            # set common histogram attributes
            hist_obj.title = name
            
            for key in ('background1','background2','n_events','n_bytes'):
                setattr(hist_obj,key,int(np.sum(getattr(hist[name],key))))
                
            for key in ('id_number','n_bins','good_bin1','good_bin2','t0_bin',
                        't0_ps','s_per_bin','fs_per_bin','htype'):
                
                item = getattr(hist[name],key)
                if all(item[0] == item):
                    setattr(hist_obj,key,item[0])
                else:
                    setattr(hist_obj,key,np.nan)
                
            # save in dictionary
            hist_joined[name] = hist_obj
        
        self.hist = hist_joined
    
    # ======================================================================= #
    def _combine_values(self,name,x):
        """
            Combine and return attributes of underlying data 
            
            name:   key associated with attribute
            x:      array of values to combine
        """
        
        if type(x) in (np.ndarray,mlist):
            
            x = np.asarray(x)
            
            if name == 'mean':          return np.mean(x)
            elif name == 'std':         return np.sum(x**2)**0.5
            elif name == 'skew':        return np.nan
            elif name == 'high':        return np.max(x)
            elif name == 'low':         return np.min(x)
            
            elif name == 'duration':    return int(np.sum(x))
                          
            elif name in ('end_date',
                          'end_time'):  return x[-1]
                          
            elif name in ('start_date',
                          'start_time'):return x[0]
            
            elif name == 'experimenter':
                
                # remove duplicates
                all_names = []
                for i in x:
                    all_names.extend(re.split('[:, ]',i))
                all_names = np.unique(all_names)
                all_names = all_names[all_names!='']
                return ', '.join(all_names)
                
            elif name in ('apparatus',
                          'area',
                          'das',
                          'lab',
                          'method',
                          'mode',
                          'orientation',
                          'sample',
                          'units',
                          'description',
                          'title',
                          'id_number',
                          'exp',
                          'title'):
                if all(x == x[0]):      return x[0]
                else:                   return 'non-matching ("' + str(x[0]) + \
                                               '" + others)'
        else:
            return x
