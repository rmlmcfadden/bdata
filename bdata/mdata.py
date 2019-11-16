# Python base class for reading MUD files. 
# Derek Fujimoto
# Nov 2019

import bdata.mudpy as mp
import numpy as np
import time

__doc__="""
    mud-data module. The mdata object is a data container, designed to read out 
    the MUD data files and to provide user-friendly access to MUD data. The MUD 
    data file is read and closed on object construction. 
    
    Signature: mdata(filename)
    
    Features -----------------------------------------------------------------
    
        Representation 
    
            Representation has been nicely formatted so that typing the object 
            name into the interpreter produces nice output. 
        
        Operators
            
            mvar, mscaler, and mhist objects allow for arithmatic or logic 
            operators to be used, where the value used in the operation is the 
            mean, count, or data array respectively. 
            
        Special Rules For Attributes
        
            If an attribute is not found in mdata, it will look for the 
            attribute in the mdict objects in the order: hist, ivar, sclr
            This second-level attribute search is much slower than regular 
            access.
            
            mdict objects all allow assignment and fetching of dictionary keys 
            as if they were attributes. Note that one can replace "+" with "p",
            and "-" with "m" to allow fetching of histograms. 
        
    Derek Fujimoto
    Nov 2019
    """

# =========================================================================== #
class mdata(object):
    """
        Data fields
            apparatus       str, name of spectrometer
            area            str, name of area data was taken
            das             str, data aquisition software
            description     str, run description
            duration        int, length of run
            end_date        str, end of run human-readable string
            end_time        int, end of run epoch time 
            exp             int, experiment number
            experimenter    str, experimenter names
            hist            mhist, histograms
            ivar            mhist, independent variables
            lab             str, facility name
            method          str, name of data collection method
            mode            str, run mode (insert)
            orientation     str, sample orientation
            run             int, run number
            sample          str, sample name
            start_date      str, start of run human-readable string 
            start_time      int, start of run epoch time 
            title           str, run title
            year            int, year at start of run
            
        Private worker functions
            __init__
            __getattr__
            __repr__
    """
    
    # link object attributes with mudpy function (attribute:function)
    # must have a title attribute
    description_attribute_functions = { 
                            'description':mp.get_description,
                            'exp':mp.get_exp_number,
                            'run':mp.get_run_number,
                            'duration':mp.get_elapsed_seconds,
                            'start_time':mp.get_start_time,
                            'end_time':mp.get_end_time,
                            'title':mp.get_title,
                            'lab':mp.get_lab,
                            'area':mp.get_area,
                            'method':mp.get_method,
                            'apparatus':mp.get_apparatus,
                            'mode':mp.get_insert,
                            'sample':mp.get_sample,
                            'orientation':mp.get_orientation,
                            'das':mp.get_das,
                            'experimenter':mp.get_experimenter,
                            'temperature':mp.get_temperature,
                            'field':mp.get_field,
                            }
    
    histogram_attribute_functions = {
                            'title':mp.get_hist_title,
                            'htype':mp.get_hist_type,
                            'data':mp.get_hist_data,
                            'n_bytes':mp.get_hist_n_bytes,
                            'n_bins':mp.get_hist_n_bins,
                            'n_events':mp.get_hist_n_events,
                            'fs_per_bin':mp.get_hist_fs_per_bin,
                            's_per_bin':mp.get_hist_sec_per_bin,
                            't0_ps':mp.get_hist_t0_ps,
                            't0_bin':mp.get_hist_t0_bin,
                            'good_bin1':mp.get_hist_good_bin1,
                            'good_bin2':mp.get_hist_good_bin2,
                            'background1':mp.get_hist_background1,
                            'background2':mp.get_hist_background2,
                            }
    
    scaler_attribute_functions = {
                            'counts':mp.get_scaler_counts,
                            'title':mp.get_scaler_label,
                            }   
    
    variable_attribute_functions = {
                            'low':mp.get_ivar_low,
                            'high':mp.get_ivar_high,
                            'mean':mp.get_ivar_mean,
                            'std':mp.get_ivar_std,
                            'skew':mp.get_ivar_skewness,
                            'title':mp.get_ivar_name,
                            'description':mp.get_ivar_description,
                            'units':mp.get_ivar_units,
                            }
    
    comment_attribute_functions = {
                            'title':mp.get_comment_title,
                            'time':mp.get_comment_time,
                            'author':mp.get_comment_author,
                            'body':mp.get_comment_body,
                            }
                
    # ======================================================================= #    
    def __init__(self,filename):
        """Constructor. Reads file."""
        
        # Open file ----------------------------------------------------------
        try:
            fh = mp.open_read(filename)
        except RuntimeError:
            raise RuntimeError("Open file %s failed. " % filename) from None
        try:
            # Read run description
            for attr,func in self.description_attribute_functions.items():
                try:
                    setattr(self,attr,func(fh))
                except RuntimeError:
                    pass
            
            # Read histograms
            self._read_mdict(fh=fh,
                             get_n=mp.get_hists,
                             attr_dict=self.histogram_attribute_functions,
                             attr_name='hist',
                             obj_class=mhist
                             )
            
            # Read scalers
            self._read_mdict(fh=fh,
                             get_n=mp.get_scalers,
                             attr_dict=self.scaler_attribute_functions,
                             attr_name='sclr',
                             obj_class=mscaler
                             )
            
            # Read independent variables
            self._read_mdict(fh=fh,
                             get_n=mp.get_ivars,
                             attr_dict=self.variable_attribute_functions,
                             attr_name='ivar',
                             obj_class=mvar
                             )
           
            # Read comments
            self._read_mdict(fh=fh,
                             get_n=mp.get_comments,
                             attr_dict=self.comment_attribute_functions,
                             attr_name='comments',
                             obj_class=mcomment
                             )
                    
        # Close file ----------------------------------------------------------
        finally:
            mp.close_read(fh)
        
        # set the date
        try:
            self.start_date = time.ctime(self.start_time)
            self.year = time.gmtime(self.start_time).tm_year
        except AttributeError:
            pass
            
        try:
            self.end_date = time.ctime(self.end_time)
        except AttributeError:
            pass
        
    # ======================================================================= #
    def __getattr__(self,name):
        
        try:
            # fetch from top level
            return getattr(object,name)
        except AttributeError as err:
            
            # fetching of second level
            if hasattr(self,'hist') and hasattr(self.hist,name):
                return getattr(self.hist,name)
            if hasattr(self,'ivar') and hasattr(self.ivar,name): 
                return getattr(self.ivar,name)
            if hasattr(self,'sclr') and hasattr(self.sclr,name): 
                return getattr(self.sclr,name)
                    
            # nothing worked - raise error
            raise AttributeError(err) from None
                        
    # ======================================================================= #
    def __repr__(self):
        """
            Nice printing of parameters.
        """
        
        d = self.__dict__
        dkeys = list(d.keys())
        if dkeys:
            items = []
            dkeys.sort()
            for key in dkeys:
                if key[0] == '_': continue
                
                # non iterables and mdict objects
                if not hasattr(d[key],'__iter__') or d[key].__class__ == mdict:
                    items.append([key,d[key]])                
                
                # strings
                elif d[key].__class__ == str:
                    items.append([key,d[key]])                
                
                # misc objects
                else:
                    items.append([key,d[key].__class__])
                
                            
            m = max(map(len,dkeys)) + 1
            s = '\n'.join([k.rjust(m)+': '+repr(v) for k, v in sorted(items)])
            return s
        else:
            return self.__class__.__name__ + "()"
    
    # ======================================================================= #
    def _read_mdict(self,fh,get_n,attr_dict,attr_name,obj_class):
        """
            Read all of a type of objects from MUD file and set its attributes, 
            place in mdict. 
            
            fh:         file header
            get_n:      mudpy function which gets the number of objects in the file
            attr_dict:  dictionary which links attribute name and mudpy function
            attr_name:  main attribute name. Ex: hist, scaler, or ivar
            obj_class:  object class to make
        """
        try:
            n = get_n(fh)[1]
        except RuntimeError:
            pass
        else:
            setattr(self,attr_name,mdict())
            for i in range(1,n+1):
                
                obj = obj_class()
                obj.id_number = i
                
                for attr,func in attr_dict.items():
                    try:
                        setattr(obj,attr,func(fh,i))
                    except RuntimeError:
                        pass
                getattr(self,attr_name)[obj.title] = obj
        
# =========================================================================== #
# DATA CONTAINERS
# =========================================================================== #
class mcontainer(object):
    """
        Provides common functions for data containers
        
        _get_val(): return the value needed to do the various operators. 
                    Define in child classes
    """

    def __repr__(self):
        if list(self.__slots__):
            m = max(map(len,self.__slots__)) + 1
            s = ''
            s += '\n'.join([k.rjust(m) + ': ' + repr(getattr(self,k))
                              for k in sorted(self.__slots__)])
            return s
        else:
            return self.__class__.__name__ + "()"

    # arithmatic operators
    def __add__(self,other):        return self._get_val()+other
    def __sub__(self,other):        return self._get_val()-other
    def __mul__(self,other):        return self._get_val()*other
    def __div__(self,other):        return self._get_val()/other
    def __floordiv__(self,other):   return self._get_val()//other
    def __mod__(self,other):        return self._get_val()%other
    def __divmod__(self,other):     return divmod(self._get_val(),other)
    def __pow__(self,other):        return pow(self._get_val(),other)
    def __lshift__(self,other):     return self._get_val()<<other
    def __rshift__(self,other):     return self._get_val()>>other
    def __neg__(self):              return -self._get_val()
    def __pos__(self):              return +self._get_val()
    def __abs__(self):              return abs(self._get_val())
    def __invert__(self):           return ~self._get_val()
    def __round__(self):            return round(self._get_val())
    
    # casting operators
    def __complex__(self):          return complex(self._get_val())
    def __int__(self):              return int(self._get_val())
    def __float__(self):            return float(self._get_val())
    def __str__(self):              return str(self._get_val())
    
    # logic operators
    def __eq__(self,other):     
        if isinstance(other,mvar):  return self==other
        else:                       return self._get_val()==other
    def __lt__(self,other):     
        if isinstance(other,mvar):  return self._get_val()<other._get_val()
        else:                       return self._get_val()<other
    def __le__(self,other):
        if isinstance(other,mvar):  return self._get_val()<=other._get_val()
        else:                       return self._get_val()<=other
    def __gt__(self,other):
        if isinstance(other,mvar):  return self._get_val()>other._get_val()
        else:                       return self._get_val()>other
    def __ge__(self,other):
        if isinstance(other,mvar):  return self._get_val()>=other._get_val()
        else:                       return self._get_val()>=other
    
    def __and__(self,other):
        if isinstance(other,mvar):  return self&other
        else:                       return self._get_val()&other
    def __xor__(self,other):
        if isinstance(other,mvar):  return self^other
        else:                       return self._get_val()^other
    def __or__(self,other):
        if isinstance(other,mvar):  return self|other
        else:                       return self._get_val()|other
    
    # reflected operators
    def __radd__(self,other):       return self.__add__(other)        
    def __rsub__(self,other):       return self.__sub__(other)        
    def __rmul__(self,other):       return self.__mul__(other)     
    def __rdiv__(self,other):       return self.__div__(other)    
    def __rfloordiv__(self,other):  return self.__floordiv__(other)
    def __rmod__(self,other):       return self.__mod__(other)      
    def __rdivmod__(self,other):    return self.__divmod__(other)
    def __rpow__(self,other):       return self.__pow__(other)      
    def __rlshift__(self,other):    return self.__lshift__(other)
    def __rrshift__(self,other):    return self.__rshift__(other)                          
    def __rand__(self,other):       return self.__and__(other)
    def __rxor__(self,other):       return self.__xor__(other)
    def __ror__(self,other):        return self.__or__(other)    

# =========================================================================== #
class mdict(dict):
    """
        Provides common functions for dictionaries of data containers
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as err:
            name = name.replace('n','-').replace('p','+')
            try:
                return self[name]
            except KeyError:
                raise AttributeError(err) from None

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    
    def __repr__(self):
        klist = list(self.keys())
        if klist:
            klist.sort()
            s = self.__class__.__name__+': {'
            for k in self.keys():
                s+="'"+k+"'"+', '
            s = s[:-2]
            s+='}'
            return s
        else:
            return self.__class__.__name__ + "()"
    
    def __dir__(self):
        return list(self.keys())

# =========================================================================== #
class mcomment(mcontainer):
    """
        Comment with mdata object.
        
        Data fields:
            id_number
            author
            body
            title
            time
    """
    __slots__ = ('id_number','author', 'body', 'title', 'time')
    
# =========================================================================== #
class mhist(mcontainer):
    """
        Histogram associated with mdata object.
        
        Data fields:
            id_number
            htype 
            title
            data
            n_bytes
            n_bins
            n_events
            fs_per_bin
            s_per_bin
            t0_ps
            t0_bin
            good_bin1
            good_bin2
            background1
            background2
    """
    
    __slots__ = ('id_number', 'htype', 'title', 'data', 'n_bytes', 'n_bins', 
                 'n_events', 'fs_per_bin', 's_per_bin', 't0_ps', 't0_bin', 
                 'good_bin1', 'good_bin2', 'background1', 'background2')
    
    def _get_val(self):     return self.data
    def astype(self,type):  return self.data.astype(type)
    
# =========================================================================== #
class mscaler(mcontainer):
    """
        Scaler associated with mdata object.
        
        Data fields:
            id_number
            title
            counts
    """
    __slots__ = ('id_number','title','counts')
    
    def _get_val(self): return self.counts
        
# ========================================================================== #
class mlist(list):
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
            out = mlist([getattr(d,name) for d in self])
            
            # if base level, return as array
            if type(out[0]) in (float,int):
                return np.array(out)
            else:
                return out
    
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
            out = mlist([d[name] for d in self])

            # if base level, return as array
            if type(out[0]) in (float,int):
                return np.array(out)
            else:
                return out

# =========================================================================== #
class mvar(mcontainer):
    """
        Independent variable associated with bdata object.
        
        Data fields:
            id_number
            low
            high
            mean
            std
            skew
            title
            description
            units
    """
        
    __slots__ = ('id_number', 'low', 'high', 'mean', 'std', 'skew', 'title', 
                 'description', 'units')

    def _get_val(self): return self.mean
            
