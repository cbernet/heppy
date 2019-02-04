'''TFile service, to create root file common to all analyzers.
'''

from heppy.framework.services.service import Service
from ROOT import TFile

class TFileService(Service):
    """TFile service.
    
    Create a root file that can be used by all analyzers.
    Even though this possibility exists, it is often better to declare
    and fill specific output root files in each analyzer.  
    
    Example::

        output_rootfile = cfg.Service(
          TFileService,
          'myhists',
          fname='histograms.root',
          option='recreate'
        )
        
    @param fname: Name of the output root file.
    @param option: Passed to the TFile constructor.
    
    """
    def __init__(self, cfg, comp, outdir):
        """
        comp is a dummy parameter here.  
        It is needed because the looper creates services and analyzers 
        in the same way, providing the configuration (cfg), 
        the component currently processed (comp), 
        and the output directory. 

        Other implementations of the TFileService could 
        make use of the component information, eg. the component name. 
        """
        fname = '/'.join([outdir, cfg.fname])
        self.file = TFile(fname, cfg.option)
        
    def stop(self):
        '''Write and close the file.'''
        self.file.Write() 
        self.file.Close()

