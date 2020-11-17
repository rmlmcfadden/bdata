# Python object for reading bnmr and bnqr msr data files. 
# Requires use of the mudpy package.
# Derek Fujimoto
# July 2017

import bdata as bd
import numpy as np
import pandas as pd
import os, glob
import datetime, warnings, requests

from mudpy import mdata
from mudpy.containers import mdict, mvar, mhist

__doc__="""
    Beta-data module. The bdata object is largely a data container, designed to 
    read out the MUD data files and to provide user-friendly access to 
    BNMR/BNQR data. Data files are read either from a directory specified by 
    environment variable (see below), or from a passed filename for easy 
    external user access. In this case, data files can be downloaded from 
    musr.ca. The MUD data file is read and closed on object construction. 
    
    Signature: bdata(run_number, year=None, filename='')
    
    Example usage ------------------------------------------------------------
    
        import bdata as bd
        b = bd.bdata(40001)                 # read run 40001 from current year. 
        b = bd.bdata(40001, year=2009)       # read run 40001 from year 2009.
        b = bd.bdata(0, filename='file.msr') # read file from local memory, run 
                                              number unused.
    Methods ------------------------------------------------------------------
    
        b.asym()            # calculate asymmetry. See bdata.asym docstring.     
        b.beam_kev()        # returns beam energy in keV
        b.pulse_off_s()     # pulse-off time for SLR measurements: 

    Setup --------------------------------------------------------------------
    
        bdata will download the mssr data files from musr.ca automatically and 
        save them under the install location by default. 
        
        To specify the data directory, set environment variables BNMR_ARCHIVE 
        and BNQR_ARCHIVE such that one can access the msr files according to 
        the following scheme:
        
        ${BNMR_ARCHIVE}/year/filename
        ${BNQR_ARCHIVE}/year/filename

        This may be preferred if access to data prior to archival is desired. 

    Features -----------------------------------------------------------------
    
        Representation 
    
            Representation has been nicely formatted so that typing the object 
            name into the interpreter produces nice output. 
        
        Operators
            
            mvar, mscaler, and mhist objects allow for arithmatic or logic 
            operators to be used, where the value used in the operation is the 
            mean, count, or data array respectively. 
            
            Example:    b.ppg.bias15 + 1       
            is equivalent to 
                        b.ppg.bias15.mean + 1
        
        Special Rules For Attributes
        
            If an attribute is not found in bdata, it will look for the 
            attribute in the mdict objects in the order: camp, epics, ppg, hist.
            This second-level attribute search is much slower than regular 
            access.
            
            mdict objects all allow assignment and fetching of dictionary keys 
            as if they were attributes. Note that one can replace "+" with "p", 
            and "-" with "m" to allow fetching of histograms. 
        
            Example: b.ppg.beam_on, bd.ppg['beam_on'], bd.beam_on all have the 
                     exact same output, with the last being much slower than 
                     the others.
    
    Derek Fujimoto
    Nov 2019
"""

# =========================================================================== #
class bdata(mdata):
    """
        Class fields 
            dkeys
            evar_bnmr
            evar_bnqr
            
        Data fields
            ppg
            epics
            camp
            + inherited fields from mdata
                        
        Public functions
            asym
            beam_kev
            pulse_off_s
            
        Private worker functions
            __init__
            __getattr__
            __repr__
            __setattr__
            _get_area_data
            _get_asym_hel
            _get_asym_comb
            _get_asym_alpha
            _get_asym_alpha_tag
            _get_1f_sum_scans
            _get_2e_asym
            _get_ppg
            _get_xhist
            _rebin
    """
    
    # set nice dictionary keys 
    dkeys = {
        
        # PPG (just the stuff after the last "/")
            "e20 beam on dwelltimes"            :"beam_on", 
            "e00 beam on dwelltimes"            :"beam_on", 
            "e20  beam off dwelltimes"          :"beam_off", 
            "e20 beam off dwelltimes"           :"beam_off",   
            "e00 beam off dwelltimes"           :"beam_off",   
            "beam off time (ms)"                :"beam_off_ms", 
                                                        
            "constant time between cycles"      :"const_t_btwn_cycl", 
            "e1f const time between cycles"     :"const_t_btwn_cycl", 
            
            "Custom var enabled"                :"customv_enable", 
            "Custom var read name"              :"customv_name_read",    
            "Custom var write name"             :"customv_name_write",    
            "Start custom scan"                 :"customv_scan_start",    
            "Stop custom scan"                  :"customv_scan_stop",    
            "Custom Increment"                  :"customv_scan_incr", 
                                                        
            "DAQ drives sampleref"              :"smpl_ref_daq_drive", 
            "DAQ service time (ms)"             :"service_t", 
            "Dwell time (ms)"                   :"dwelltime", 
            "Bin width (ms)"                    :"dwelltime", 
                                                        
            "Enable helicity flipping"          :"hel_enable", 
            "Enable RF"                         :"rf_enable", 
            "enable sampleref mode"             :"smpl_ref_enable", 
            
            "Field start (Gauss)"               :"field_start", 
            "Field stop (Gauss)"                :"field_stop",    
            "Field inc (Gauss)"                 :"field_incr", 
            
            "frequency increment (Hz)"          :"freq_incr", 
            "frequency start (Hz)"              :"freq_start", 
            "frequency stop (Hz)"               :"freq_stop", 
            
            "init mode file"                    :"init_mode", 
            "init mode"                         :"init_mode", 
                                                        
            "helicity flip sleep (ms)"          :"hel_sleep", 
            "Helicity flip sleep(ms)"           :"hel_sleep", 
                                                                                                    
            "NaVolt start (volts)"              :"volt_start", 
            "NaVolt stop (volts)"               :"volt_stop", 
            "NaVolt inc (volts)"                :"volt_incr", 
                                                        
            "num bins"                          :"nbins", 
            "num cycles per supercycle"         :"ncycles", 
            "Number dwelltimes per freq"        :"ndwell_per_f", 
            "number of midbnmr regions"         :"nregion", 
            "num post RF beamOn dwelltimes"     :"ndwell_post_on", 
                                   
            "Param X Start"                     :'xstart', 
            "Param X Stop"                      :'xstop', 
            "Param X Incr"                      :'xincr', 
            "Constant param Y"                  :'yconst', 
            
            "f1 frequency function"             :"freqfn_f1", 
            "f2 frequency function"             :"freqfn_f2", 
            "f3 frequency function"             :"freqfn_f3", 
            "f4 frequency function"             :"freqfn_f4", 
                                                        
            "PPG mode"                          :"mode",     
            "e20 prebeam dwelltimes"            :"prebeam", 
            "e00 prebeam dwelltimes"            :"prebeam", 
            "psm onef enabled"                  :"onef_enable", 
            "psm onef scale factor"             :"onef_scale", 
            "psm fREF enabled"                  :"fref_enable", 
            "psm fREF scale factor"             :"fref_scale", 
            "psm scale factor"                  :"psm_scale", 
            "psm scaler factor"                 :"psm_scale", 
                                                        
            "randomize freq increments"         :"rand_freq_incr", 
            "Randomize freq values"             :"rand_freq_val", 
            "Ref tuning freq (Hz)"              :"ref_tune_freq", 
            "Ref tuning frequency (Hz)"         :"ref_tune_freq", 
            "e20 rf frequency (Hz)"             :"freq", 
            "e00 rf frequency (Hz)"             :"freq", 
            "RFon delay (dwelltimes)"           :"rf_on_delay", 
            "num RF on delays (dwell times)"    :"rf_on_delay", 
            "RFon duration (dwelltimes)"        :"rf_on", 
            "RF on time (ms)"                   :"rf_on_ms", 
            "RF enabled"                        :"rf_enable", 
            
            "Single tone simulated"             :"sgle_tone_sim", 
                                                        
            "use defaults for midbnmr"          :"defaults", 
             
        # CAMP
            "/biasV/input1"                             :"rb_cell_bias_set", 
            "/biasV/output1"                            :"rb_cell_bias_read", 
        
            "/CryoEx_MassFlow/read_flow"                :"cryo_read", 
            "/CryoEx_MassFlow/set_flow"                 :"cryo_set", 
            "/Cryo_level/He_level"                      :"cryo_he", 
            "/Cryo_level/N2_level"                      :"cryo_n2", 
            "/cryo_lift/set_position"                   :"clift_set",  
            "/cryo_lift/read_position"                  :"clift_read", 
            
            "/Cryo_oven/current_read_1"                 :"oven_current", 
            "/Cryo_oven/output_1/D"                     :"oven_out_d", 
            "/Cryo_oven/output_1/I"                     :"oven_out_i", 
            "/Cryo_oven/output_1/P"                     :"oven_out_p", 
            "/Cryo_oven/read_A"                         :"oven_readA", 
            "/Cryo_oven/read_B"                         :"oven_readB", 
            "/Cryo_oven/read_C"                         :"oven_readC", 
            "/Cryo_oven/read_D"                         :"oven_readD", 
            "/Cryo_oven/setpoint_1"                     :"oven_set1", 
                        
            "/Dac0/dac_set"                             :"dac_set", 
            "/dac/dac_set"                              :"dac_set", 
            "/Dewar/He_level"                           :"he_level", 
             
            "/flow_set/output"                          :"flow_set_out", 
                                                    
            "/He_flow/read_flow"                        :"he_read", 
            "/He_flow/set_flow"                         :"he_set", 
                                                    
            "/lock-in/R"                                :"lockin_r", 
            "/lock-in/theta"                            :"lockin_theta", 
            "/lock-in/X"                                :"lockin_x", 
            "/lock-in/Y"                                :"lockin_y", 
                                                    
            "/Magnet/mag_field"                         :"b_field",     
            "/Magnet/mag_set"                           :"b_field_setpt",     
            "/Magnet/mag_read"                          :"mag_current", 
            "/Magnet/controls/sys_status"               :"mag_ctrl_status", 
            "/Magnet/volts"                             :"mag_voltage", 
            "/mass_flow/read_flow"                      :"mass_read", 
            "/mass_flow/set_flow"                       :"mass_set",   
                                                    
            "/needle-valve/read_position"               :"needle_read", 
            "/Needle/read_position"                     :"needle_pos", 
            "/Needle/motor_position"                    :"needle_pos", 
            "/needle-valve/set_position"                :"needle_set", 
            "/Needle_Valve/set_position"                :"needle_set", 
            "/Needle/set_position"                      :"needle_set", 
            
            "/PVac/adc_read"                            :"vac", 
                                                    
            "/rfamp/fwd_max"                            :"rfamp_fwd", 
            "/rfamp/fwd_power"                          :"rfamp_fpwr", 
            "/rfamp/refl_max"                           :"rfamp_rfl", 
            "/rfamp/RF_gain"                            :"rfamp_rfgain", 
            "/rf_level_cont/dac_set"                    :"rf_dac", 
                                                    
            "/Sample/current_read_1"                    :"smpl_current", 
            "/Sample/current_read"                      :"smpl_current", 
            "/Sample1/current_read"                     :"smpl_current", 
            "/Sample/read_A"                            :"smpl_read_A", 
            "/Sample1/read_A"                           :"smpl_read_A", 
            "/Sample/read_B"                            :"smpl_read_B", 
            "/Sample1/read_B"                           :"smpl_read_B", 
            "/adc0/adc_read"                            :"smpl_read_B", 
            "/Sample/read_C"                            :"smpl_read_C", 
            "/Sample/read_D"                            :"smpl_read_D", 
            "/Sample/set_current"                       :"smpl_set_current", 
            "/Sample/setpoint"                          :"smpl_set", 
            "/Sample1/setpoint"                         :"smpl_set", 
            "/Sample/setpoint_1"                        :"smpl_set", 
            "/sample2/heat_range"                       :"smpl2_heat", 
            "/sample2/sample_read"                      :"smpl2_read", 
            "/sample_volts/reading"                     :"smpl_volts", 
            "/Shield/read_1"                            :"shield_read1", 
            "/signal_gen/amplitude"                     :"sig_gen_amp", 
            "/signal_gen/frequency"                     :"sig_gen_freq", 
            "/signal_gen/power_level"                   :"sig_gen_pwr", 
            "/signal_gen/rf_on"                         :"sig_gen_rfon", 
            "/stealth/fwd_max"                          :"stealth_fwd_max", 
            "/stealth/fwd_power"                        :"stealth_fwd_pwr", 
            "/stealth/rev_max"                          :"stealth_rev_max", 
            "/stealth/rev_power"                        :"stealth_rev_pwr", 
            
        # EPICS
            "BNMR:HVBIAS:P"                             :"nmr_bias", 
            "BNMR:HVBIAS:PO"                            :"nmr_bias", 
            "BNMR:HVBIAS:POS"                           :"nmr_bias", 
            "BNMR:HVBIAS:POS:"                          :"nmr_bias", 
            "BNMR:HVBIAS:POS:R"                         :"nmr_bias", 
            "BNMR:HVBIAS:POS:RDVO"                      :"nmr_bias", 
            "BNMR:HVBIAS:POS:RDVOL"                     :"nmr_bias", 
            "BNMR:HVBIAS:POS:RDVOL1"                    :"nmr_bias", 
                                                  
            "BNMR:HVBIAS:N"                             :"nmr_bias_n", 
            "BNMR:HVBIAS:NE"                            :"nmr_bias_n", 
            "BNMR:HVBIAS:NEG"                           :"nmr_bias_n", 
            "BNMR:HVBIAS:NEG:"                          :"nmr_bias_n", 
            "BNMR:HVBIAS:NEG:R"                         :"nmr_bias_n", 
            "BNMR:HVBIAS:NEG:RDVO"                      :"nmr_bias_n", 
            "BNMR:HVBIAS:NEG:RDVOL"                     :"nmr_bias_n", 
            "BNMR:HVBIAS:NEG:RDVOL1"                    :"nmr_bias_n", 
                                                  
            "BNQR:HVBIAS:RD"                            :"nqr_bias", 
            "BNQR:HVBIAS:RDVOL"                         :"nqr_bias", 
                                                  
            "ITE:BIAS:RDVO"                             :"target_bias",  
            "ITE:BIAS:RDVOL"                            :"target_bias",  
            "ITE:BIAS:RDVOLER"                          :"target_bias",  
            "ITE:BIAS:RDVOLVOL"                         :"target_bias", 
            "ITW:BIAS:R"                                :"target_bias", 
            "ITW:BIAS:RD"                               :"target_bias", 
            "ITW:BIAS:RDV"                              :"target_bias", 
            "ITW:BIAS:RDVO"                             :"target_bias", 
            "ITW:BIAS:RDVOL"                            :"target_bias", 
            "ITW:BIAS:RDVOL1"                           :"target_bias", 
            "ITW:BIAS:RDVOLVOL"                         :"target_bias", 
                                                  
            "ILE2:BIAS15:R"                             :"bias15", 
            "ILE2:BIAS15:RD"                            :"bias15", 
            "ILE2:BIAS15:RDV"                           :"bias15", 
            "ILE2:BIAS15:RDVO"                          :"bias15",    
            "ILE2:BIAS15:RDVOL"                         :"bias15", 
                                                  
            "ILE2:LAS:RDPO"                             :"las_pwr", 
            "ILE2:LAS:RDPOW"                            :"las_pwr", 
            "ILE2:LAS:RDPOWE"                           :"las_pwr", 
            "ILE2:LAS:RDPOWER"                          :"las_pwr", 
            "ILE2:LAS:RDPOWERL"                         :"las_pwr", 
             
            "ILE2:BIASTUBE:"                            :"biastube", 
            "ILE2:BIASTUBE:V"                           :"biastube", 
            "ILE2:BIASTUBE:VOL"                         :"biastube", 
             
            "ILE2:DPPLR:CH0:HW:RDVOL"                   :"dopplertube", 
             
            "ILE2A1:HH:CUR"                             :"hh_current", 
            "ILE2A1:HH:RDCU"                            :"hh_current", 
            "ILE2A1:HH:RDCUR"                           :"hh_current", 
            "ILE2A1:HH3:RDCUR"                          :"hh_current", 
            "":""
            }
    
    
    option = {  ''                      :'',
                
                'adif'                  :'alpha_diffusion',
                'ad'                    :'alpha_diffusion',
                'adiff'                 :'alpha_diffusion',
                'alpha_diffusion'       :'alpha_diffusion',
                
                'atag'                  :'alpha_tagged',
                'at'                    :'alpha_tagged',
                'alpha_tagged'          :'alpha_tagged',
                
                'b'                     :'backward_counter',
                'bck'                   :'backward_counter',
                'backward_counter'      :'backward_counter',
                'left'                  :'backward_counter',
                'left_counter'          :'backward_counter',
                
                'c'                     :'combined',
                'com'                   :'combined',
                'combined'              :'combined',
                
                'cntr'                  :'counter',
                'counter'               :'counter',
                
                'dif_c'                 :'difference_combined', 
                'dc'                    :'difference_combined', 
                'difference_combined'   :'difference_combined', 
                
                'dif_h'                 :'difference_helicity',
                'dh'                    :'difference_helicity',
                'difference_helicity'   :'difference_helicity',
                
                'f'                     :'forward_counter',
                'fwd'                   :'forward_counter',
                'forward_counter'       :'forward_counter',
                'right'                 :'forward_counter',
                'right_counter'         :'forward_counter',
                
                '+'                     :'positive', 
                'up'                    :'positive', 
                'u'                     :'positive', 
                'p'                     :'positive',
                'pos'                   :'positive', 
                'positive'              :'positive',
                
                '-'                     :'negative',
                'down'                  :'negative', 
                'd'                     :'negative',
                'n'                     :'negative',
                'neg'                   :'negative',
                'negative'              :'negative',
                
                'h'                     :'helicity',
                'hel'                   :'helicity',
                'helicity'              :'helicity',
                
                'r'                     :'raw',
                'raw'                   :'raw',
                
                'raw_c'                 :'raw_combined',
                'rc'                    :'raw_combined',
                'raw_combined'          :'raw_combined',
                
                'raw_h'                 :'raw_helicity',
                'rh'                    :'raw_helicity',
                'raw_helicity'          :'raw_helicity',
                
                'sl_c'                  :'slope_combined',
                'slc'                   :'slope_combined', 
                'sc'                    :'slope_combined',
                'slope_combined'        :'slope_combined',
                
                'sl_h'                  :'slope_helicity',
                'slh'                   :'slope_helicity',
                'sh'                    :'slope_helicity',
                'slope_helicity'        :'slope_helicity',
    }
    
    # set environment variable same to get data archive location
    # should point to something like
    # "/data1/bnmr/dlog/" on linbnmr2
    # "/data/bnmr/" on muesli or lincmms
    evar_bnmr = "BNMR_ARCHIVE"
    evar_bnqr = "BNQR_ARCHIVE"
    
    # ======================================================================= #
    def __init__(self, run_number, year=None, filename=""):
        """Constructor. Reads file, stores and sorts data."""
            
        # convert dkeys keys to lower case
        bdata.dkeys = {k.lower():i for k, i in self.dkeys.items()}
            
        # Get the current year
        if year is None:   year = datetime.datetime.now().year
        
        # read file if not provided
        if filename == "":
            
            # Get spectrometer directory. Based on rmlm's bnmr_20a.cpp.
            if run_number >= 40000 and run_number <= 44999:
                spect_dir = "bnmr"
            elif run_number >= 45000 and run_number <= 49999:
                spect_dir = "bnqr"
            else:
                raise ValueError("Run number out of range") 
                
            # look for data location
            if spect_dir == "bnmr":
                
                use_default_dir = not self.evar_bnmr in os.environ
                if use_default_dir:
                    directory = os.path.join(bd._mud_data, spect_dir)
                else:
                    directory = os.environ[self.evar_bnmr]
                    
            elif spect_dir == "bnqr":
                
                use_default_dir = not self.evar_bnqr in os.environ
                if use_default_dir:
                    directory = os.path.join(bd._mud_data, spect_dir)
                else:
                    directory = os.environ[self.evar_bnqr]
                    
            # finalize file name
            run = '%06d.msr' % run_number
            filename = os.path.join(directory, str(year), run)
            
            # if file does not exist, try to fetch from web
            if not os.path.isfile(filename):
                
                # make directory 
                os.makedirs(os.path.join(directory, str(year)), exist_ok=True)
                
                # make url
                url = '/'.join(('http://musr.ca/mud/data', 
                                spect_dir.upper(), 
                                str(year), 
                                run))
            
                # get data
                webfile = requests.get(url)
                if not webfile.ok:
                    raise RuntimeError('File %s not found. '%filename+\
                                'Attempted download from musr.ca failed.')
                
                # write to file
                with open(filename, 'wb') as fid:
                    fid.write(webfile.content)
                
                # let users know what happened
                warnings.warn('Run %d (%d) not found '% (run_number, year)+\
                              'locally. Fetched and saved to %s '%directory+\
                              'from musr.ca.', 
                              category=Warning)
                        
        # Open and read file
        super().__init__(filename)
        
        # cast histogram data to floats
        for key, hist in self.hist.items():
            self.hist[key].data = hist.data.astype(np.float64)
        
        # Sort independent variables into dictionaries by title
        self.ppg = mdict()
        self.camp = mdict()
        self.epics = mdict()
        
        if hasattr(self, 'ivar'):
            
            for v in self.ivar.values(): 
                try:
                    if 'PPG' in v.title:
                        self.ppg[bdata.dkeys[v.title.split("/")[-1].lower()]] = v
                    elif v.title[0] == "/":
                        self.camp[bdata.dkeys[v.title.lower()]] = v
                    else:
                        self.epics[bdata.dkeys[v.title.lower()]] = v
                except (KeyError, IndexError):
                        message = '"%s" not found in dkeys ("%s" in "%s"). ' +\
                                    "Data in list, but not sorted to dict."
                        message = message % (v.title, v.description, v.units)
                        warnings.warn(message, RuntimeWarning, stacklevel=2)
            
        # Add missing run mode for old runs
        if year < 2005 and not self.mode and self.method == 'TI-bNMR':
            self.mode = '1f' 
            
        # Fix inconsistent area for old runs
        if year == 2003 and self.area == 'ISAC':
            if self.run >= 45000:
                self.area = 'BNQR'
            else:
                self.area = 'BNMR'
            
        # Fix histogram titles for old runs
        if year == 2003 and 'FREQ' in self.hist.keys(): 
            keymap = {'FREQ':'Frequency', 
                      'Bp':'B+', 
                      'Fp':'F+', 
                      'Bm':'B-', 
                      'Fm':'F-', 
                      'FluM':'FluM2', 
                      'PolLp':'L+', 
                      'PolRp':'R+', 
                      'PolLm':'L-', 
                      'PolRm':'R-', 
                      'NBMBp':'NBMB+', 
                      'NBMFp':'NBMF+', 
                      'NBMBm':'NBMB-', 
                      'NBMFm':'NBMF-', 
                      }
            self.hist = mdict({i:self.hist[k] for k, i in keymap.items()})
            for k in self.hist.keys():
                self.hist[k].title = k
            
        # prevent overwriting of attributes
        self._bdata_initialised = True

    # ======================================================================= #
    def __getattr__(self, name):
        
        try:
            # fetch from top level
            return getattr(object, name)
        except AttributeError as err:
            
            # fetching of second level
            if hasattr(self.camp, name): return getattr(self.camp, name)
            if hasattr(self.epics, name):return getattr(self.epics, name)
            if hasattr(self.ppg, name):  return getattr(self.ppg, name)
            if hasattr(self.hist, name): return getattr(self.hist, name)
                    
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
                
                # exceptions
                if key in ('ivar', 'sclr'):
                    items.append([key, d[key].__class__])                
                    
                # non iterables and mdict objects
                elif not hasattr(d[key], '__iter__') or d[key].__class__ == mdict:
                    items.append([key, d[key]])                
                
                # strings
                elif d[key].__class__ in (str, np.str_):
                    items.append([key, d[key]])                
                
                # misc objects
                else:
                    items.append([key, d[key].__class__])
                
                            
            m = max(map(len, dkeys)) + 1
            s = '\n'.join([k.rjust(m)+': '+repr(v) for k, v in sorted(items)])
            return s
        else:
            return self.__class__.__name__ + "()"
        
    # ======================================================================= #
    def __setattr__(self, name, value):
        """Allow setting attributes only when initializing"""
        
        # this test allows attributes to be set in the __init__ method
        if '_bdata__initialised' not in self.__dict__.keys(): 
            return dict.__setattr__(self, name, value)
            
        # any normal attributes are handled normally
        elif name in self.__dict__.keys():       
            raise AttributeError('Object is readonly')
        else:
            dict.__setattr__(self, name, value)
    
    # ======================================================================= #
    def _get_area_data(self, nbm=False):
        """Get histogram list based on area type. 
        List pattern: [type1_hel+, type1_hel-, type2_hel+, type2_hel-]
        where type1/2 = F/B or R/L in that order.
        """
        
        hist = self.hist
        
        if self.mode == '1n' or nbm:
            data = [hist['NBMF+'].data, \
                    hist['NBMF-'].data, \
                    hist['NBMB+'].data, \
                    hist['NBMB-'].data]
            
        elif self.area == 'BNMR':
            data = [hist['F+'].data, \
                    hist['F-'].data, \
                    hist['B+'].data, \
                    hist['B-'].data]
        
        elif self.area == 'BNQR':
            data = [hist['R+'].data, \
                    hist['R-'].data, \
                    hist['L+'].data, \
                    hist['L-'].data]
        else:
            data = []
        
        if self.mode == '2h':
            data.extend([hist['AL1+'].data, hist['AL1-'].data, 
                         hist['AL0+'].data, hist['AL0-'].data, 
                         hist['AL3+'].data, hist['AL3-'].data, 
                         hist['AL2+'].data, hist['AL2-'].data])
        
        # copy
        return [np.copy(d) for d in data]

    # ======================================================================= #
    def _get_asym_cntr(self, d):
        """
            Find the asymmetry of each counter using the asymmetries. 
        """
        
        # get data [1+ 1- 2+ 2-] ---> [1+ 1- 2+  2-]
        d0 = d[0]; d1 = d[1]; d2 = d[2]; d3 = d[3]

        # pre-calcs
        denom1 = d0+d1; 
        denom2 = d2+d3
        
        # check for div by zero
        denom1[denom1==0] = np.nan          
        denom2[denom2==0] = np.nan
        
        # asymmetries in both helicities
        asym = [(d0-d1)/denom1, 
                (d2-d3)/denom2]
                    
        # errors 
        # https://www.wolframalpha.com/input/?i=%E2%88%9A(F*(derivative+of+((F-B)%2F(F%2BB))+with+respect+to+F)%5E2+%2B+B*(derivative+of+((F-B)%2F(F%2BB))+with+respect+to+B)%5E2)
        asym_err = [2*np.sqrt(d0*d1/np.power(denom1, 3)), 
                    2*np.sqrt(d2*d3/np.power(denom2, 3))]
        
        # remove nan            
        for i in range(2):
            asym[i][np.isnan(asym[i])] = 0.
            asym_err[i][np.isnan(asym_err[i])] = 0.
        
        # exit
        return [[asym[0], asym_err[0]],  
                [asym[1], asym_err[1]]]  
    
    # ======================================================================= #
    def _get_asym_hel(self, d):
        """
            Find the asymmetry of each helicity. 
        """
        
        # get data [1+ 1- 2+ 2-] ---> [1+ 2+ 1- 2-]
        d0 = d[0]; d1 = d[2]; d2 = d[1]; d3 = d[3]

        # pre-calcs
        denom1 = d0+d1; 
        denom2 = d2+d3
        
        # check for div by zero
        denom1[denom1==0] = np.nan          
        denom2[denom2==0] = np.nan
        
        # asymmetries in both helicities
        asym_hel = [(d0-d1)/denom1, 
                    (d2-d3)/denom2]
                    
        # errors 
        # https://www.wolframalpha.com/input/?i=%E2%88%9A(F*(derivative+of+((F-B)%2F(F%2BB))+with+respect+to+F)%5E2+%2B+B*(derivative+of+((F-B)%2F(F%2BB))+with+respect+to+B)%5E2)
        asym_hel_err = [2*np.sqrt(d0*d1/np.power(denom1, 3)), 
                        2*np.sqrt(d2*d3/np.power(denom2, 3))]
        
        # remove nan            
        for i in range(2):
            asym_hel[i][np.isnan(asym_hel[i])] = 0.
            asym_hel_err[i][np.isnan(asym_hel_err[i])] = 0.
        
        # exit
        return [[asym_hel[0], asym_hel_err[0]],  
                [asym_hel[1], asym_hel_err[1]]]  
                
    # ======================================================================= #
    def _get_asym_comb(self, d):
        """
        Find the combined asymmetry for slr runs. Elegant 4-counter method.
        """
        
        # get data [1+ 1- 2+ 2-] ---> [1+ 2+ 1- 2-]
        d0 = d[0]; d1 = d[2]; d2 = d[1]; d3 = d[3]
        
        # pre-calcs
        r_denom = d0*d3
        r_denom[r_denom==0] = np.nan
        r = np.sqrt((d1*d2/r_denom))
        r[r==-1] = np.nan
    
        # combined asymmetry
        asym_comb = (r-1)/(r+1)
        
        # check for div by zero
        d0[d0==0] = np.nan                  
        d1[d1==0] = np.nan
        d2[d2==0] = np.nan
        d3[d3==0] = np.nan
        
        # error in combined asymmetry
        asym_comb_err = r*np.sqrt(1/d1 + 1/d0 + 1/d3 + 1/d2)/np.square(r+1)
        
        # replace nan with zero 
        asym_comb[np.isnan(asym_comb)] = 0.
        asym_comb_err[np.isnan(asym_comb_err)] = 0.
        
        return [asym_comb, asym_comb_err]

    # ======================================================================= #
    def _get_asym_alpha(self, a, b):
        """
            Find alpha diffusion ratios from cryo oven with alpha detectors. 
            a: list of alpha detector histograms (each helicity)
            b: list of beta  detector histograms (each helicity)
        """
        
        # just  use AL0
        try:
            a = a[2:4]
        except IndexError:
            a = a[:2]
            
        # sum counts in alpha detectors
        asum = np.sum(a, axis=0)
        
        # sum counts in beta detectors
        bsum = np.sum(b, axis=0)
        
        # check for dividing by zero 
        asum[asum == 0] = np.nan
        bsum[bsum == 0] = np.nan
        
        # asym calcs
        asym = asum/bsum
        
        # errors
        dasym = asym*np.sqrt(1/asum + 1/bsum)
        
        return [asym, dasym]

    # ======================================================================= #
    def _get_asym_alpha_tag(self, a, b):
        """
            Find asymmetry from cryo oven with alpha detectors. 
            a: list of alpha detector histograms (each helicity)  
            b: list of beta  detector histograms (each helicity)  1+ 1- 2+ 2-
        """

        # beta in coincidence with alpha
        coin = a[:4]
        
        # beta coincidence with no alpha
        no_coin = a[4:8]

        # get split helicity asym from 
        hel_coin =      self._get_asym_hel(coin)
        hel_no_coin =   self._get_asym_hel(no_coin)
        hel_reg =       self._get_asym_hel(b)
        
        # get combined helicities
        com_coin =      self._get_asym_comb(coin)
        com_no_coin =   self._get_asym_comb(no_coin)
        com_reg =       self._get_asym_comb(b)

        # make output
        return (hel_coin, hel_no_coin, hel_reg, com_coin, com_no_coin, com_reg)

    # ======================================================================= #
    def _get_1f_sum_scans(self, d, freq):
        """
            Sum counts in each frequency bin over 1f scans, excluding zero. 
        """
        
        # make data frame
        df = pd.DataFrame({i:d[i] for i in range(len(d))})
        df['x'] = freq
        
        # combine scans: values with same frequency 
        df = df.groupby('x').sum()
        x = df.index.values
        d = df.values.T
        
        return (x, d)
        
    # ======================================================================= #
    def _get_1f_mean_scans(self, d, freq):
        """
            Average counts in each frequency bin over 1f scans. 
        """
        
        # make data frame
        df = pd.DataFrame({i:d[i] for i in range(len(d))})
        df['x'] = freq
        
        # combine scans: values with same frequency 
        df = df.groupby('x').apply(lambda i: i[i>0].mean())
        df.drop('x', axis='columns', inplace=True)
        x = df.index.values
        d = df.values.T
        
        return (x, d)
        
    # ======================================================================= #
    def _get_2e_asym(self):
        """
            Get asymmetries for 2e random-frequency scan. 
            Based on bnmr_2e.cpp by rmlm (Oct 4, 2017).
        """
        
        # get needed PPG parameters for splitting 1D histos into 2D histos
        try:        
            # get frequency vector
            freq = np.arange(self._get_ppg('freq_start'), \
                        self._get_ppg('freq_stop')+self._get_ppg('freq_incr'), \
                        self._get_ppg('freq_incr'))
                             
            # number of dwelltimes per frequency bin 
            ndwell = 2*int(self._get_ppg('ndwell_per_f'))-1
            
            # number of RF on delays for the start bin. 
            start_bin = int(self._get_ppg('rf_on_delay'))
            
            # get bin centers in ms
            time = self._get_ppg('rf_on_ms')*(np.arange(ndwell)+0.5-ndwell/2.)
            
            # get the time and index of the middle time 
            mid_time_i = int(np.floor(ndwell/2.))
            mid_time = time[mid_time_i]
        
            # beam off time after pulse in ms
            beam_off = int(self._get_ppg('beam_off_ms'))
        
        except KeyError:
            raise RuntimeError("Not all dictionary variables read out to "+\
                               "proper locations")
            
        # setup output
        out = mdict()
        out['freq'] = freq
        out['time'] = time
            
        # get data
        data = np.array(self._get_area_data()) # [[fp], [fm], [bp], [bm]]
        
        # discared initial bad bins, and beam-off trailing bins
        data = data[:, start_bin:len(freq)*ndwell+start_bin]
        
        # split data by frequency
        nsplit = len(data[0])/ndwell
        
        fp = np.array(np.split(data[0], nsplit))
        fm = np.array(np.split(data[1], nsplit))
        bp = np.array(np.split(data[2], nsplit))
        bm = np.array(np.split(data[3], nsplit))
        
        # get raw asymmetries 
        asym_p_2cntr = (bp-fp)/(bp+fp)      # two counter
        asym_m_2cntr = (bm-fm)/(bm+fm)      # two counter
        r = np.sqrt(bp*fm/(bm*fp))
        asym_4cntr = (r-1)/(r+1)            # four counter
        
        # get raw asymmetry errors
        asym_p_2cntr_err = 2*np.sqrt(bp*fp)/((bp+fp)**1.5)
        asym_m_2cntr_err = 2*np.sqrt(bm*fm)/((bm+fm)**1.5)
        asym_4cntr_err = r*np.sqrt(1./bp+1./bm+1./fp+1./fm)/((r+1)**2)

        # save to output
        out['raw_p'] = np.array([asym_p_2cntr, asym_p_2cntr_err])
        out['raw_n'] = np.array([asym_m_2cntr, asym_m_2cntr_err])
        out['raw_c'] = np.array([asym_4cntr, asym_4cntr_err])

        # wrap asymmetry arrays into one for calculations [p, m, 4]
        # indexing is now [pm4][freq][time bin]
        asym     = np.array([asym_p_2cntr,    asym_m_2cntr,    asym_4cntr])
        asym_err = np.array([asym_p_2cntr_err, asym_m_2cntr_err, asym_4cntr_err])

        # compute differenced asymmetries via slopes from weighted least squares 
        # minimization.
        if ndwell >= 5:
            
            # calculate needed components element-wise
            w = asym_err**-2
            x = time
            y = asym
            
            wx = w*x
            wy = w*y
            wxy = w*x*y
            wxx = w*x*x
        
            # sum over values i < mid_time_i within each asymmetry and frequency 
            # Indexing: [pm4][freq]
            w_pre   = np.sum(w  [:, :, :mid_time_i], 2)    
            wx_pre  = np.sum(wx [:, :, :mid_time_i], 2)
            wy_pre  = np.sum(wy [:, :, :mid_time_i], 2)
            wxy_pre = np.sum(wxy[:, :, :mid_time_i], 2)
            wxx_pre = np.sum(wxx[:, :, :mid_time_i], 2)
            
            # sum over values i > mid_time_i
            w_pst   = np.sum(w  [:, :, -mid_time_i:], 2)
            wx_pst  = np.sum(wx [:, :, -mid_time_i:], 2)
            wy_pst  = np.sum(wy [:, :, -mid_time_i:], 2)
            wxy_pst = np.sum(wxy[:, :, -mid_time_i:], 2)
            wxx_pst = np.sum(wxx[:, :, -mid_time_i:], 2)
            
            # calculate slopes and intercepts
            delta_pre = w_pre*wxx_pre - wx_pre**2
            delta_pst = w_pst*wxx_pst - wx_pst**2
            
            sl_pre = (w_pre*wxy_pre - wx_pre*wy_pre)/delta_pre
            sl_pst = (w_pst*wxy_pst - wx_pst*wy_pst)/delta_pst
            dsl_pre = np.sqrt(w_pre/delta_pre)
            dsl_pst = np.sqrt(w_pst/delta_pst)
            
            intr_pre = (wy_pre*wxx_pre - wx_pre*wxy_pre)/delta_pre
            intr_pst = (wy_pst*wxx_pst - wx_pst*wxy_pst)/delta_pst
            dintr_pre = np.sqrt(wxx_pre/delta_pre)
            dintr_pst = np.sqrt(wxx_pst/delta_pst)
            
            # extrapolate to middle time bin
            asym_slopes = intr_pst-intr_pre+(sl_pst-sl_pre)*mid_time
            asym_slopes_err = np.sqrt(dintr_pre**2 + dintr_pst**2 + \
                                      (dsl_pre**2 + dsl_pst**2) * mid_time**2)
            
            # save to output        
            out['sl_p'] = np.array([asym_slopes[0], asym_slopes_err[0]])
            out['sl_n'] = np.array([asym_slopes[1], asym_slopes_err[1]])
            out['sl_c'] = np.array([asym_slopes[2], asym_slopes_err[2]])
        
        # calculate asymmetry using differences
        asym_diff = asym[:, :, mid_time_i+1] - asym[:, :, mid_time_i-1]
        asym_diff_err = np.sqrt(asym_err[:, :, mid_time_i+1]**2+\
                                asym_err[:, :, mid_time_i-1]**2)
        
        # save to output
        out['dif_p'] = np.array([asym_diff[0], asym_diff_err[0]])
        out['dif_n'] = np.array([asym_diff[1], asym_diff_err[1]])
        out['dif_c'] = np.array([asym_diff[2], asym_diff_err[2]])   
            
        return out

    # ======================================================================= #
    def _get_ppg(self, name):
        """Get ppg parameter mean value"""
        return self.ppg[name].mean
    
    # ======================================================================= #
    def _get_xhist(self):
        """Get histogram data for x axis."""
        if self.mode == '1f':
            xlabel = 'Frequency'
        elif self.mode == '1w':
            xlabel = 'x parameter'
        elif self.mode == '1n':
            for xlabel in self.hist.keys():
                if 'cell' in xlabel.lower():    
                    break
        elif self.mode == '1e':
            xlabel = 'Magnet mA'
        
        return self.hist[xlabel].data
    
    # ======================================================================= #
    def _rebin(self, xdx, rebin):
        """
            Rebin array x with weights 1/dx**2 by factor rebin.
            
            Inputs: 
                xdx = [x, dx]
                rebin = int
            Returns [x, dx] after rebinning. 
        """

        x = xdx[0]
        dx = xdx[1]
        rebin = int(rebin)
        
        # easy end condition
        if rebin <= 1:
            return (x, dx)
        
        # Rebin Discard unused bins
        lenx = len(x)
        x_rebin = []
        dx_rebin = []
        
        # avoid dividing by zero
        dx[dx==0] = np.inf
        
        # weighted mean
        for i in np.arange(0, lenx, rebin):
            w = 1./dx[i:i+rebin-1]**2
            wsum = np.sum(w)
            
            if wsum == 0:
                x_rebin.append(np.mean(x[i:i+rebin-1]))
                dx_rebin.append(np.std(x[i:i+rebin-1]))
            else:
                x_rebin.append(np.sum(x[i:i+rebin-1]*w)/wsum)
                dx_rebin.append(1./wsum**0.5)
        return np.array([x_rebin, dx_rebin])
            
    # ======================================================================= #
    def asym(self, option="", omit="", rebin=1, hist_select='', nbm=False):
        """Calculate and return the asymmetry for various run types. 
           
        usage: asym(option="", omit="", rebin=1, hist_select='', nbm=False)
            
        Inputs:
            option:         see below for details
            omit:           1f bins to omit if space seperated string in options 
                                is not feasible. See options description below.
            rebin:          SLR only. Weighted average over 'rebin' bins to 
                                reduce array length by a factor of rebin. 
            hist_select:    string to specify which histograms get combined into 
                                making the asymmetry calculation. Deliminate 
                                with [, ] or [;]. Histogram names cannot 
                                therefore contain either of these characters.
            nbm:            if True, use neutral beams in calculations
            
        Asymmetry calculation outline (with default detectors) ---------------
        
            Split helicity      (NMR): (F-B)/(F+B) for each
            Combined helicity   (NMR): (r-1)/(r+1)
                where r = sqrt([(B+)(F-)]/[(F+)(B-)])
            Split counter       (NMR): (+ - -)/(+ + -) for each F, B
            
            
            
            Split helicity      (NQR): (R-L)/(R+L) for each
            Combined helicity   (NQR): (r-1)/(r+1)
                where r = sqrt([(L+)(R-)]/[(R+)(L-)])
            Split counter       (NMR): (+ - -)/(+ + -) for each R, L
            
            Alpha diffusion     (NQR) sum(AL0)/sum(L+R)
            Alpha tagged        (NQR) same as NQR, but using the tagged counters
            
        Histogram Selection ---------------------------------------------------
        
            If we wished to do a simple asymmetry calculation in the form of 
                                    
                                    (F-B)/(F+B)
            
            for each helicity, then 
                                       |--|  |--|   paired counter location
                        hist_select = 'F+, F-, B+, B-'
                                        |-----|       paired helicities
                                           |-----|
            
            for alpha diffusion calculations append the two alpha counters
            
                hist_select = 'R+, R-, L+, L-, A+, A-
            
            for alpha tagged calculations do the following
            
                hist_select = 'R+, R-, L+, L-, TR+, TR-, TL+, TL-, nTR+, nTR-, nTL+, nTL-'
                    
                where TR is the right counter tagged (coincident) with alphas, 
                      TL is the left  counter tagged with alphas, 
                     nTR is the right counter tagged with !alphas (absence of), 
                     nLR is the right counter tagged with !alphas, 
                                          
                  
        Status of Data Corrections --------------------------------------------
            SLR/2H: 
                Removes prebeam bins. 
                
                Rebinning: 
                    returned time is average time over rebin range
                    returned asym is weighted mean
                
            1F/1W: 
                Allows manual removal of unwanted bins. 
                
                Scan Combination:
                    Multiscans are considered as a single scan with long 
                    integration time. Histogram bins are summed according to 
                    their frequency bin, errors are Poissonian.
                    
                    In the case of split counter asymmetries, we take the mean
                    of the non-zero counts in each bin, with errors treated still
                    as Possionian.
            
            1N:
                Same as 1F. Uses the neutral beam monitor values to calculate 
                asymetries in the same manner as the NMR calculation. 
             
            2E: 
                Prebeam bin removal. 
                Postbeam bin removal. Assumes beamoff time is 0. 
                Splits saved 1D histograms into 2D.
                
                Asymmetry calculations: 
                    raw: calculated through differences method (as described in 
                        the asymmetry calculation outline)
                    dif: let 0 be the index of the centermost scan in time. dif 
                        asymmetries are then calculated via raw[i+1]-raw[i-1], 
                        where "raw" is as calculated in the above line, for each 
                        of the three types: +, -, combined 
                    sl: take a weighted least squares fit to the two bins prior 
                        and the two bins after the center bin (in time). For 
                        each find the value of the asymmetry at the center time 
                        position. Take the difference: post-prior
                    
        Option List
        
            SLR DESCRIPTIONS --------------------------------------------------
            
            "":     dictionary of 2D numpy arrays keyed by 
                        {"p", "n", "c", "time_s"} for each helicity and combination 
                        (val, err). Default return state for unrecognized options
            "h":    dictionary 2D numpy arrays keyed by {"p", "n", "time_s"} for 
                        each helicity (val, err).
            "p":    2D np array of up helicity state [time_s, val, err].
            "n":    2D np array of down helicity state [time_s, val, err].
            "c":    2D np array of combined asymmetry [time_s, val, err].
            "ad":   2D np array of alpha diffusion ratio [time_s, val, err].
            "at":   dictionary of alpha tagged asymmetries key:[val, err]. 
                    Keys:
                        
                        'time_s'               : 1D array of times in seconds   
                        'p_wiA', 'n_wiA', 'c_wiA': coincident with alpha
                        'p_noA', 'n_noA', 'c_noA': coincident with no alpha
                        'p_noT', 'n_noT', 'c_noT': untagged
                        
                where p, n, c refer to pos helicity, neg helicity, combined 
                helicity respectively. Only in 2h mode. 
                        
            
            1F DESCRIPTIONS ---------------------------------------------------
            
                all options can include a space deliminated list of bins or 
                ranges of bins which will be omitted. ex: "raw 1 2 5-20 3"
            
            "":     dictionary of 2D numpy arrays keyed by {p, n, c, freq} for each 
                        helicity and combination [val, err]. Default return state 
                        for unrecognized options.
            "r":    Dictionary of 2D numpy arrays keyed by {p, n} for each 
                        helicity (val, err), but listed by bin, not combined by 
                        frequency. 
            "h":    get unshifted +/- helicity scan-combined asymmetries as a 
                        dictionary {'p':(val, err), 'n':(val, err), 'freq'}
            "p":    get pos helicity states as tuple, combined by frequency 
                        (freq, val, err)
            "n":    similar to p but for negative helicity states
            "c":    get combined helicity states as tuple (freq, val, err)
            
                        
            2E DESCRIPTIONS ---------------------------------------------------
            
            "sc":   get slope combined helicity states as tuple (freq, val, err)
            "dc":   get difference combined helicity states as tuple (freq, val, err)
            "rc":   get raw combined helicity states as tuple (freq, time, val, err)
            
                If no options, returns a dictionary with the keys: 
             
            'dif_p':    [val, err][frequency] of pos. helicity asymmetry 
            'dif_n':    [ve][f] of negative helicity asymmetry
            'dif_c':    [ve][f] of combined helicity asymmetry
            
            'raw_p':    [ve][f][time] raw asymmetries of each time bin. Pos hel. 
            'raw_n':    [ve][f][t] negative helicity.
            'raw_c':    [ve][f][t] combined helicity
            
            'freq':     [f] frequency values
            'time':     [t] time bin values
                
            'sl_p':     [ve][f] pos. hel. of asymmetry calcuated through slopes 
                            of pre and post middle time bin. Slope method only 
                            for >= 5 time bins, corresponds to >= 3 RF on delays
            'sl_n':     [ve][f] negative helicity.
            'sl_c':     [ve][f] combined helicity.
        """
        
        # check rebin factor
        if type(rebin) not in (int, np.int64) or rebin < 1:
            raise RuntimeError('Rebinning factor must be int >= 1.')
        
        # check for additonal options (1F)
        if omit != '':
            further_options = list(map(str.strip, omit.split(' ')))
        else:
            further_options = list(map(str.strip, option.split(' ')[1:]))
        option = option.split(' ')[0].strip()
        
        # Option reduction
        option = option.lower()
        try:
            option = self.option[option]
        except KeyError:
            raise RuntimeError("Option not recognized.")
        
        # get data
        if hist_select != '':
            
            # split into parts
            hist_select_temp = []
            for histname in hist_select.split(', '):
                hist_select_temp.extend(histname.split(';'))
            hist_select = [h.strip() for h in hist_select_temp]
            
            # check for user error
            if len(hist_select) < 4:
                raise RuntimeError('hist_select must be a string of at least '+\
                        'four [, ]-seperated or [;]-seperated histogram names')
            
            # get data
            d = [self.hist[h].data for h in hist_select]
            d_all = d
            
        # get default data
        else:
            d = self._get_area_data(nbm=nbm) # 1+ 2+ 1- 2-
            d_all = d
            
        # get alpha diffusion data
        if self.mode == '2h':
            d_alpha = d[4:]
            d = d[:4]
        
        # SLR -----------------------------------------------------------------
        if self.mode in ("20", '2h'):
            
            # get the number of prebeam bins
            try:
                n_prebeam = int(self._get_ppg('prebeam'))
            
            # some old runs don't log prebeam values
            except KeyError:
                pass
            
            # remove negative count values, delete prebeam entries
            else:
                
                bad_ppg_prebeam = False
                for i in range(len(d)):
                    d[i][d[i]<0] = 0.
                    d[i] = np.delete(d[i], np.arange(n_prebeam))
                    
                    # check that prebeams were set correctly 
                    # (in 2019 some NQR run are off by one)
                    if d[i][0] < 20:
                        bad_ppg_prebeam = True
                
                # if prebeams not set properly, remove the first bin (off by one error)
                if bad_ppg_prebeam:
                    warnings.warn("%d.%d: Detected a " % (self.year, self.run)+\
                        'mismatch between the ppg prebeams setting and the '+\
                        'histogram counts. Removing an extra bin to account '+\
                        'for a prebeam off-by-one error (known to exist for '+\
                        '2018-2020 B-NQR 20 and 2e runs)')
                                                    
                    for i in range(len(d)):
                        d[i] = np.delete(d[i], [0])
                        
            # do alpha background subtractions
            if self.mode == '2h':    
                for i in range(len(d_alpha)):
                    d_alpha[i][d_alpha[i]<0] = 0.
                    d_alpha[i] = np.delete(d_alpha[i], np.arange(n_prebeam))
                
            # get helicity data
            if option not in ('combined', 'forward_counter', 'backward_counter'):
                h = np.array(self._get_asym_hel(d))
            elif option in ('forward_counter', 'backward_counter'):
                h = np.array(self._get_asym_cntr(d))
                
            # rebin time
            time = (np.arange(len(d[0]))+0.5)*self._get_ppg('dwelltime')/1000
            
            if rebin > 1:
                len_t = len(time)
                new_time = (np.average(time[i:i+rebin-1]) for i in np.arange(0, len_t, rebin))
                time = np.fromiter(new_time, dtype=float, count=int(len_t/rebin))

            # mode switching
            if option in ('positive', 'forward_counter'): # ---------------------------------------
                return np.vstack([time, self._rebin(h[0], rebin)])
                
            elif option in ('negative', 'backward_counter'): # -------------------------------------
                return np.vstack([time, self._rebin(h[1], rebin)])
            
            elif option == 'helicity': # -------------------------------------
                out = mdict()
                out['p'] = self._rebin(h[0], rebin)
                out['n'] = self._rebin(h[1], rebin)
                out['time_s'] = time
                return out
                
            elif option == 'counter': # -------------------------------------
                out = mdict()
                out['fwd'] = self._rebin(h[0], rebin)
                out['bck'] = self._rebin(h[1], rebin)
                out['time_s'] = time
                return out
                
            elif option == 'combined': # -------------------------------------
                c = np.array(self._get_asym_comb(d))
                return np.vstack([time, self._rebin(c, rebin)])
                
            elif option == 'alpha_diffusion': # ------------------------------
                try:
                    asym = self._get_asym_alpha(d_alpha, d)
                except UnboundLocalError as err:
                    if self.mode != '2h':
                        raise RuntimeError('Run is not in 2h mode.')
                return np.vstack([time, self._rebin(asym, rebin)])
            
            elif option == 'alpha_tagged': # ---------------------------------
                try:
                    asym = self._get_asym_alpha_tag(d_alpha, d)  
                except UnboundLocalError as err:
                    if self.mode != '2h':
                        raise RuntimeError('Run is not in 2h mode.')
                    else:
                        raise err
                
                out = mdict()
                out['p_wiA'] = self._rebin(asym[0][0], rebin)
                out['n_wiA'] = self._rebin(asym[0][1], rebin)
                out['p_noA'] = self._rebin(asym[1][0], rebin)
                out['n_noA'] = self._rebin(asym[1][1], rebin)
                out['p_noT'] = self._rebin(asym[2][0], rebin)
                out['n_noT'] = self._rebin(asym[2][1], rebin)
                out['c_wiA'] = self._rebin(asym[3], rebin)
                out['c_noA'] = self._rebin(asym[4], rebin)
                out['c_noT'] = self._rebin(asym[5], rebin)
                out['time_s'] = time
                
                return out
            
            else:
                h = np.array(self._get_asym_hel(d))
                c = np.array(self._get_asym_comb(d))
                ctr = np.array(self._get_asym_cntr(d))
                
                out = mdict()
                out['p'] = self._rebin(h[0], rebin)
                out['n'] = self._rebin(h[1], rebin)
                out['fwd'] = self._rebin(ctr[0], rebin)
                out['bck'] = self._rebin(ctr[1], rebin)
                out['c'] = self._rebin(c, rebin)  
                out['time_s'] = time
                return out
        
        # 1F ------------------------------------------------------------------
        elif self.mode in ('1f', '1n', '1w', '1e'):
            
            # get xaxis label and data key
            if self.mode == '1f':
                xlab = 'freq'
            elif self.mode == '1w':
                xlab = 'xpar'
            elif self.mode == '1n':
                xlab = 'mV'
            elif self.mode == '1e':
                xlab = 'mA'
            
            # get bins to kill
            bin_ranges_str = further_options 
            bin_ranges = []
            for b in bin_ranges_str:
                if not '-' in b:
                    bin_ranges.append(int(b))
                else:
                    one = int(b.split('-')[0])
                    two = int(b.split('-')[1])
                    bin_ranges.extend(np.arange(one, two+1))
            
            # kill bins
            for i in range(len(d)):

                # get good bin range
                if len(bin_ranges) > 0:
                    bin_ranges = np.array(bin_ranges)
                    idx = (bin_ranges>=0)*(bin_ranges<len(d[i]))
                    bin_ranges = bin_ranges[idx]

                # kill
                d[i][bin_ranges] = 0.
            
            # get frequency
            freq = self._get_xhist()
            
            # mode switching
            if option =='raw':
                a = self._get_asym_hel(d)
                out = mdict()
                out['p'] = np.array(a[0])
                out['n'] = np.array(a[1])
                out[xlab] = np.array(freq)
                return out 
            elif option in ('counter', 'forward_counter', 'backward_counter'):
                freq_cntr, d_cntr = self._get_1f_mean_scans(d, freq)
            if option == '':
                freq_cntr, d_cntr = self._get_1f_mean_scans(d, freq)
                freq, d = self._get_1f_sum_scans(d, freq)
            else:
                freq, d = self._get_1f_sum_scans(d, freq)
                                       
            # rebin frequency
            if rebin>1:
                len_f = len(freq)
                newf = (np.average(freq[i:i+rebin-1]) for i in np.arange(0, len_f, rebin))
                freq = np.fromiter(newf, dtype=float, count=int(np.ceil(len_f/rebin)))
                                       
            # swtich between remaining modes
            if option == 'helicity':
                a = self._get_asym_hel(d)
                out = mdict()
                out['p'] = self._rebin(a[0], rebin)
                out['n'] = self._rebin(a[1], rebin)
                out[xlab] = np.array(freq)
                return out
            
            elif option == 'positive':
                a = self._get_asym_hel(d)
                return np.vstack([freq, self._rebin(a[0], rebin)])
            
            elif option == 'negative':
                a = self._get_asym_hel(d)
                return np.vstack([freq, self._rebin(a[1], rebin)])
            
            elif option == 'counter':
                a = self._get_asym_cntr(d_cntr)
                out = mdict()
                out['fwd'] = self._rebin(a[0], rebin)
                out['bck'] = self._rebin(a[1], rebin)
                out[xlab] = np.array(freq_cntr)
                return out
            
            elif option == 'forward_counter':
                a = self._get_asym_cntr(d_cntr)
                return np.vstack([freq_cntr, self._rebin(a[0], rebin)])
            
            elif option == 'backward_counter':
                a = self._get_asym_cntr(d_cntr)
                return np.vstack([freq_cntr, self._rebin(a[1], rebin)])
            
            elif option in ['combined']:
                a = self._get_asym_comb(d)
                return np.vstack([freq, self._rebin(a, rebin)])
                
            else:
                ah = self._get_asym_hel(d)
                ac = self._get_asym_comb(d)
                ctr = self._get_asym_cntr(d_cntr)
                
                out = mdict()
                out['p'] = self._rebin(ah[0], rebin)
                out['n'] = self._rebin(ah[1], rebin)
                out['fwd'] = self._rebin(ctr[0], rebin)
                out['bck'] = self._rebin(ctr[1], rebin)
                out['c'] = self._rebin(ac, rebin)  
                out[xlab] = np.array(freq)
                out[xlab+'_cntr'] = np.array(freq_cntr)
                
                return out
            
        # 2E ------------------------------------------------------------------
        elif self.mode in ('2e', ):
            adict = self._get_2e_asym()
            
            if option == 'slope_combined':  
                return (adict['freq'], *adict['sl_c'])
            elif option == 'difference_combined':  
                return (adict['freq'], *adict['dif_c'])
            elif option == 'raw_combined':  
                return (adict['freq'], adict['time'], *adict['raw_c'])
            else:
                return adict
        
        # unknown entry -------------------------------------------------------
        else:
            print("Unknown run type.")
            return

    # ======================================================================= #
    def beam_kev(self, get_error=False):
        """
            Get the beam energy in kev, based on typical biases: 
                itw (or ite bias) - bias15 - platform bias
                
            if get_error: fetch error in value, rather than value
        """
        
        # get epics pointer
        epics = self.epics
        
        # fetch stds
        if get_error:
            attr = 'std'
        else:
            attr = 'mean'
        
        # get inital beam energy in keV
        beam = getattr(epics.target_bias, attr)/1000.
            
        # get RB cell voltage
        bias15 = getattr(epics.bias15, attr)/1000.
        
        # get platform bias 
        if self.area == 'BNMR':
            platform = getattr(epics.nmr_bias, attr)
        elif self.area == 'BNQR':
            platform = getattr(epics.nqr_bias, attr)/1000.
        else:
            raise RuntimeError('Area not recognized')
        
        if get_error:
            return np.sqrt(np.sum(np.square((beam, bias15, platform)))) # keV
        else:
            return beam-bias15-platform # keV
    
    # ======================================================================= #
    def get_pulse_s(self):
        """Get pulse duration in seconds, for pulsed measurements."""
        
        try:
            dwelltime = self._get_ppg('dwelltime')
            beam_on = self._get_ppg('beam_on')
        except AttributeError:
            raise AttributeError("Missing logged ppg parameter: dwelltime "+\
                    "or beam_on") from None
        return dwelltime*beam_on/1000.
    
# set lifetimes for various particles in seconds, with errors (ref: rmlm slr_v2.cpp)
# commented out isotopes with multiple decay products not taken into account by bfit
life = mdict({
            "Li8"       :1.2096,    # http://journals.aps.org/prc/abstract/10.1103/PhysRevC.82.027309
            "Li8_err"   :0.0005, 
            "Li9"       :0.2572,    # http://journals.aps.org/prc/abstract/10.1103/PhysRevC.13.835
            "Li9_err"   :0.0006, 
            "Li11"      :0.0126,   # http://www.sciencedirect.com/science/article/pii/S0375947412000413
            "Li11_err"  :0.0020, 
            "Be11"      :19.85,     # http://www.sciencedirect.com/science/article/pii/S0375947412000413
            "Be11_err"  :0.10,   
            "F20"       :16.105,    # http://www.sciencedirect.com/science/article/pii/037594749290251E
            "F20_err"   :0.012,  
            "Mg29"      :1.88,     # http://www.sciencedirect.com/science/article/pii/S0375947403018074
            "Mg29_err"  :0.17,   
            "Mg31"      :0.332,     # http://www.sciencedirect.com/science/article/pii/S0375947403018074
            "Mg31_err"  :0.029,   
            "Ac230"     :175.76,    # http://isys01.triumf.ca/search/isotope/data/view?z=89&a=230&m=0
            "Ac232"     :171.43,    # http://isys01.triumf.ca/search/isotope/data/view?z=89&a=232&m=0
            "Ac234"     :63.49,     # https://www.sciencedirect.com/science/article/pii/0375947486900254
            "Ac234_err" :10.1,      # https://www.sciencedirect.com/science/article/pii/0375947486900254
        })
