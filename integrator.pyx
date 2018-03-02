# Cython functions for fast numerical integration 
# Derek Fujimoto
# October 2017
#
# Based on the work of John D. Cook
# https://www.johndcook.com/blog/double_exponential_integration/
# Note: to see slow lines write 'cython integrator.pyx -a --cplus'

# To build write: python setup_integrator.py build_ext --inplace
# assuming the cython seup file is called setup_integrator.

cimport cython
cimport numpy as np
import numpy as np
from libc.math cimport exp 

# ========================================================================== #
# Integration functions import
cdef extern from 'integration_fns.cpp':
    cdef cppclass IntegralStrExp:
        IntegralStrExp(double,double,double,double,double) except +
        double out

    cdef cppclass IntegralMixedStrExp:
        IntegralMixedStrExp(double,double,double,double,double,double,double,double) except +
        double out
        
# =========================================================================== #
# Integrator class
cdef class Integrator:
    cdef double life            # probe lifetime in s
    cdef double pulse_len       # length of beam on in s

# =========================================================================== #
    def __init__(self,lifetime,pulse_len):
        """
            Inputs:
                lifetime: probe lifetime in s
                pulse_len: beam on pulse length in s
        """
        self.life = lifetime
        self.pulse_len = pulse_len

# =========================================================================== #
    @cython.boundscheck(False)  # some speed up in exchange for instability
    def pulsed_str_exp(self,np.ndarray[double, ndim=1] time,double Lambda, 
                        double Beta, double amp, double offset):
        """
            Pulsed stretched exponential for an array of times. Efficient 
            c-speed looping and indexing. 
            
            Inputs: 
                time: array of times
                pulse_len: pulse length
                Lambda: 1/T1 in s^-1
                Beta: stretching factor
                Amp: amplitude
                Offset: constant additative offset
                
            Outputs: 
                np.array of values for the puslsed stretched exponential. 
        """
        
        # Variable definitions
        cdef double out
        cdef int n = time.shape[0]
        cdef int i
        cdef double t
        cdef np.ndarray[double, ndim=1] out_arr = np.zeros(n)
        cdef double prefac
        cdef life = self.life
        cdef pulse_len = self.pulse_len
        
        # Calculate pulsed str. exponential
        for i in xrange(n):    
            
            # get some useful values: time, normalization
            t = time[i]
            prefac = life*(1.-exp(-t/life))
        
            # prefactor special case
            if prefac == 0:
                out_arr[i] = np.inf
                continue
            
            # during pulse
            if t<pulse_len:
                x = new IntegralStrExp(t,t,Lambda,Beta,life)
                out = amp*x.out/prefac+offset
            
            # after pulse
            else:
                x = new IntegralStrExp(t,pulse_len,Lambda,Beta,life)
                out = amp/prefac*x.out*exp((t-pulse_len)/life)+offset
            
            # save result
            out_arr[i] = out
        
        return out_arr

# =========================================================================== #
    @cython.boundscheck(False)  # some speed up in exchange for instability
    def mixed_pulsed_str_exp(self,np.ndarray[double, ndim=1] time, 
                double Lambda1, double Beta1, double Lambda2, double Beta2,
                double alpha, double amp):
        """
            Pulsed stretched exponential for an array of times. Efficient 
            c-speed looping and indexing. 
            
            Inputs: 
                time: array of times
                pulse_len: pulse length
                Lambda: 1/T1 in s^-1
                Beta: stretching factor
                alpha: mixing 0 < alpha < 1
                
            Outputs: 
                np.array of values for the puslsed stretched exponential. 
        """
        
        # Variable definitions
        cdef double out
        cdef int n = time.shape[0]
        cdef int i
        cdef double t
        cdef np.ndarray[double, ndim=1] out_arr = np.zeros(n)
        cdef double prefac
        cdef life = self.life
        cdef pulse_len = self.pulse_len
        
        # Calculate pulsed str. exponential
        for i in xrange(n):    
            
            # get some useful values: time, normalization
            t = time[i]
            prefac = life*(1.-exp(-t/life))
        
            # prefactor special case
            if prefac == 0:
                out_arr[i] = np.inf
                continue
            
            # during pulse
            if t<pulse_len:
                x = new IntegralMixedStrExp(t,t,Lambda1,Beta1,Lambda2,Beta2,
                        alpha,life)
                out = amp*x.out/prefac
            
            # after pulse
            else:
                x = new IntegralMixedStrExp(t,pulse_len,Lambda1,Beta1,Lambda2,
                        Beta2,alpha,life)
                out = amp/prefac*x.out*exp((t-pulse_len)/life)
            
            # save result
            out_arr[i] = out
        
        return out_arr
