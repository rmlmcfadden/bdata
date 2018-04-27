# bdata

    Beta-data module. The bdata object is largely a data container, designed to 
    read out the MUD data files and to provide user-friendly access to reliably 
    corrected BNMR/BNQR data. Data files are read either from a directory 
    specified by environment variable (see below), or from a passed filename 
    for easy external user access. In this case, data files can be downloaded 
    from musr.ca. The MUD data file is read and closed on object construction. 
    
    Requires the installation of mudpy. See mudpy docstring for installation
    instructions. 
    
    Constructor: bdata(run_number,year=0,filename='')
    
    Example usage: 
        bd = bdata(40001)           # read run 40001 from the default year. 
        bd = bdata(40001,year=2009) # read run 40001 from 2009.
        bd = bdata(0,filename='file.msr') # read file from local memory, run 
                                            number unused 
        
    if year==0 then default is the current year. For scripts analysing a 
    specific data set, it is advised that this be set so that the script does 
    not break as time passes. 
        
    Asymmetry: 
        bd.asym() # for details and options see bdata.asym docstring. 
        
    Beam energy: 
        bd.beam_kev()   # returns beam energy in keV
               
    Pulse-off time for SLR measurements: 
        pulse_off_s()
                                      
    For a nicely-formatted list of all data fields call the fields method: 
        bd.fields()
        
        Note that the object representation has been nicely formatted as well, 
        so that typing
        
        bd
        
        into the interpreter produces nice output. 
        
    Note that bdict objects allow for the calling of dictionary keys like an 
    object attribute. For example, bd.ppg.beam_on or bd.ppg['beam_on'] have the 
    exact same output. Note that reserved characters such as '+' cannot be used 
    in this manner. 
            
    One can also set the location of the data archive via environment 
    variables "BNMR_ARCHIVE" and "BNQR_ARCHIVE". This would be something 
    like "/data1/bnmr/dlog/" on linbnmr2 or "/data/bnmr/" on muesli or 
    lincmms
        
    Derek Fujimoto
    August 2017
    
    Last updated: December 2017
