# Python object for math operations on bdata objects. 
# Derek Fujimoto
# Aug 2019
from bdata import bdict,bhist
from bdata import bdata
import numpy as np
import pandas as pd

class bjoined(bdata):
    """
        Object to store lists or the combination of bdata objects. 
        
        data:                   list of bdata objects    
        
        Math operates only on histograms. 
    """
    
    # ======================================================================= #
    def __init__(self,bdata_list):
        """
            bdata_list:               list of bdata objects
        """
        
        # set data
        self.data = bdata_list
        
        # set some calculation-required parameters
        self.set_common('mode')
        self.set_common('area')
        
        # combine the histograms
        self.combine_hist()
    
    # ======================================================================= #
    def __getattr__(self,name):
        """
            Get attribute of underlying data as a list.
        """
        try:
            # fetch from top level
            return getattr(object,name)
        except AttributeError:
            return blist([getattr(d,name) for d in self.data])

    # ======================================================================= #
    def __repr__(self):
        """
            Nice printing of parameters.
        """
        
        d = [dat.__dict__ for dat in self.data]
        dkeys = list(d[0].keys())
        if dkeys:
            items = []
            dkeys.sort()
            for key in dkeys:
                if key[0] == '_': continue
                
                if d[0][key].__class__ == bdict:
                    items.append([key,d[0][key]])
                elif not hasattr(d[0][key],'__iter__') or d[0][key].__class__ == str:
                    items.append([key,[di[key] for di in d]])                
                else:
                    items.append([key,[di[key].__class__ for di in d]])
                
                            
            m = max(map(len,dkeys)) + 1
            s = '\n'.join([k.rjust(m)+': '+repr(v) for k, v in sorted(items)])
            return s
        else:
            return self.__class__.__name__ + "()"

    # ======================================================================= #
    def _get_area_data(self,nbm=False):
        """Get histogram list based on area type. 
        List pattern: [type1_hel+,type1_hel-,type2_hel+,type2_hel-]
        where type1/2 = F/B or R/L in that order.
        """
        
        # get histogram
        hist = self.hist_joined
        
        # return data set
        if self.mode == '1n' or nbm:
            data = [hist['NBMF+'].data,\
                    hist['NBMF-'].data,\
                    hist['NBMB+'].data,\
                    hist['NBMB-'].data]
            
        elif self.area == 'BNMR':
            data = [hist['F+'].data,\
                    hist['F-'].data,\
                    hist['B+'].data,\
                    hist['B-'].data]
        
        elif self.area == 'BNQR':
            data = [hist['R+'].data,\
                    hist['R-'].data,\
                    hist['L+'].data,\
                    hist['L-'].data]
        else:
            data = []
        
        if self.mode == '2h':
            data.extend([hist['AL1+'].data,hist['AL1-'].data,
                         hist['AL0+'].data,hist['AL0-'].data,
                         hist['AL3+'].data,hist['AL3-'].data,
                         hist['AL2+'].data,hist['AL2-'].data])
        
        # copy
        return [np.copy(d) for d in data]
    
    # ======================================================================= #
    def asym_mean(self,*asym_args,**asym_kwargs):
        """
            Get individual asymmetries first, then combine with weighted mean
            
            asym_args: dict, passed to bdata.asym. 
        """
    
        # calcuate asymmetries
        asym_list = [b.asym(*asym_args,**asym_kwargs) for b in self.data]
        
        # make into dataframes, get errors as weights
        for i in range(len(asym_list)):
            asym = asym_list[i]
            
            # tuple return: (x,a,da)
            if type(asym) is np.ndarray:
                asym_list[i] = pd.DataFrame({'x':asym[0],'a':asym[1],'da':asym[2]})
            
            # dict return: (x,p:(a,da),...)
            elif type(asym) is bdict:
                
                # if entry is tuple, split into error and value
                klist = list(asym.keys())
                for k in klist:
                    if type(asym[k]) is tuple:
                        asym['d'+k] = asym[k][1]
                        asym[k] = asym[k][0]
                    else:
                        asym['x'] = asym[k]
                        del asym[k]
                        xk = k
                
                # make into data frame
                asym_list[i] = pd.DataFrame(asym)
        
        # combine the data frames and set index
        df = pd.concat(asym_list).set_index('x')
        
        # slice into errors and values
        values = pd.DataFrame(df[[c for c in df.columns if 'd' not in c]])
        errors = pd.DataFrame(df[[c for c in df.columns if 'd' in c]])
        
        # rename error columns
        errors.rename(columns={c:c.replace('d','') for c in errors.columns},
                      inplace=True)
        
        # make errors weights
        errors = 1/errors.apply(np.square)
        
        # weight the values
        values = values * errors
        
        # group and sum 
        values = values.groupby(level=0).sum()
        errors = errors.groupby(level=0).sum()

        # weighted mean
        values = values / errors
        errors = 1/errors.apply(np.sqrt)
        
        # make output type the same as the original 
        if type(asym) is np.ndarray:
            return np.array([values.index.values,
                             values.values.T[0],
                             errors.values.T[0]])
        
        elif type(asym) is bdict:
            out = bdict()
            out[xk] = values.index
            for c in values.columns:
                out[c] = (values[c].values,errors[c].values)
        
            return out
        
    # ======================================================================= #
    def combine_hist(self):
        """
            Apply np.sum to base histograms and set result to top level
            
            Scans are concatenated. 
            SLR histograms are summed.
        """
        
        # these will get combined
        hist_names = ('F+','F-','B+','B-',
                      'L+','L-','R+','R-',
                      'NBMF+','NBMF-','NBMB+','NBMB-')
        
        # these modes require appending scans rather than averaging
        hist_xnames = ('Frequency','x parameter',)
        
        # set these fields to nan
        nan_fields = ('background1','background2','good_bin1','good_bin2',
                      't0_bin','t0_ps','s_per_bin','fs_per_bin','n_bytes',
                      'htype')
        
        # make container
        hist_joined = bdict()
        
        # check if x values in histogram
        do_append = any([h in self.hist[0] for h in hist_xnames])
        
        # get x histogram name
        if do_append:
            for xname in hist_xnames: 
                if xname in self.hist[0]: 
                    break
            
        for name in hist_names:
            
            # name doesn't exist
            if name not in self.hist[0].keys(): continue
            
            # combine scan-less runs (just add the histogrms)
            if not do_append:
                hist_data = np.sum(list(self.hist[name].data),axis=0)
            
            # combine runs with scans (append the data)
            else:                
                hist_data = np.concatenate(self.hist[name].data)
                x = np.concatenate(self.hist[xname].data)                
                
            # make the object
            hist_obj = bhist()
            hist_obj.id_number = self.hist[0][name].id_number
            hist_obj.title = name
            hist_obj.n_bins = self.hist[0][name].n_bins
            hist_obj.n_events = np.sum(list(self.hist[name].n_events))
            hist_obj.data = hist_data
                    
            for f in nan_fields:    setattr(hist_obj,f,np.nan)
            
            # save in dictionary
            hist_joined[name] = hist_obj
        
        # make x histogram
        if do_append:
        
            # make the object
            hist_obj = bhist()
            hist_obj.id_number = self.hist[0][xname].id_number
            hist_obj.title = name
            hist_obj.n_bins = self.hist[0][xname].n_bins
            hist_obj.n_events = np.sum(list(self.hist[xname].n_events))
            hist_obj.data = x
            
            for f in nan_fields:    setattr(hist_obj,f,np.nan)
            
            # save in dictionary
            hist_joined[xname] = hist_obj
        
        self.hist_joined = hist_joined
    
    # ======================================================================= #
    def get_ppg(self,name):
        """Get ppg parameter mean value"""
        
        values = self.ppg[name].mean
        if not all([values[0] == v for v in values]):
            raise RuntimeError('PPG Parameter %s not equal in all cases' % name)

        return values[0]
    
    # ======================================================================= #
    def get_xhist(self):
        """Get histogram data for x axis."""
        if self.mode == '1f':
            xlabel = 'Frequency'
        elif self.mode == '1w':
            xlabel = 'x parameter'
        elif self.mode == '1n':
            for xlabel in self.hist.keys():
                if 'cell' in xlabel.lower():    
                    break
        
        return self.hist_joined[xlabel].data
    
    # ======================================================================= #
    def set_common(self,name):
        """
            Set attribute which is shared among all joine data sets.
        """
        
        item_list = getattr(self,name)
        if all([item_list[0] == i for i in item_list]):
            setattr(self,name,item_list[0])
        else:
            raise RuntimeError('Expected attribute %s to be ' % name+\
                                'common among data sets')
    
# ========================================================================== #
class blist(list):
    """
        List object from which attributes/keys are accessed from each element, 
        then returned as a list
    """
    
    # ======================================================================= #
    def __getattr__(self,name):
        """
            Get attribute of underlying data as a list.
        """
        
        # fetch from top level
        try:
            return getattr(object,name)
        # fetch from lower levels
        except AttributeError:
            return blist([getattr(d,name) for d in self])
    
    # ======================================================================= #
    def __getitem__(self,name):
        """
            Get attribute of underlying data as a list.
        """
        # fetch from top level
        try:
            return list.__getitem__(self,name)
        
        # fetch from lower levels
        except TypeError:
            return blist([d[name] for d in self])

        


