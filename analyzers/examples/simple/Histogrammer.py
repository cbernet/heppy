'''Demonstrates how to write out an histogram using the
L{TFile service<heppy.framework.services.tfile>}'''

from heppy.framework.analyzer import Analyzer
from ROOT import TH1F

class Histogrammer(Analyzer):
    '''Demonstrate how to write out an histogram using the L{TFile service<heppy.framework.services.tfile>}.
    
    Example::
    
      tfile_service_1 = cfg.Service(
          TFileService,
          'tfile1',
          fname='histograms.root',
          option='recreate'
        )

      histogrammer = cfg.Analyzer(
        Histogrammer,
        file_label = 'tfile1'
      )
    
    '''

    def beginLoop(self, setup):
        super(Histogrammer, self).beginLoop(setup)
        servname = '_'.join(['heppy.framework.services.tfile.TFileService',
                             self.cfg_ana.file_label
                         ]) 
        tfileservice = setup.services[servname]
        tfileservice.file.cd()
        self.hist = TH1F("hist", "an histogram", 200, 0, 200)
        
    def process(self, event):
        self.hist.Fill(event.iEv)
    
