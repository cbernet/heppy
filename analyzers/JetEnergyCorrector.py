'''Creates a collection of calibrated jets.'''
from heppy.framework.analyzer import Analyzer

import copy

class JetEnergyCorrector(Analyzer):
    '''Creates a collection of calibrated jets
 
    Example::
    
        from heppy.analyzers.JetEnergyCorrector import JetEnergyCorrector
        from papas.detectors.CMS import CMS
        cms_roc.set_working_point(0.7)
        jec = cfg.Analyzer(
            ParametrizedBTagger,
            output = 'jets_corr',
            input_jets = 'jets',
            detector = CMS
        )
  
    @param input_jets: input collection of jets. 
    @param detector: L{detector, like CMS<heppy.papas.detectors.CMS.CMS>}.
      The detector has the method jet_energy_correction(jet), returning
      the scaling factor.
      
    The 4-momentum of the calibrated jet is obtained by scaling
    the 4-momentum of the input jet. 
    '''
    def process(self, event):
        '''Process the event.
        
        The event must contain:
         - the collection of jets to be corrected.
         
        Produces the output collection event.<self.cfg_ana.output>,
        containing a copy of each input jet, with a corrected energy
        '''
        jets = getattr(event, self.cfg_ana.input_jets)
        jets_rescaled = []
        for jet in jets:
            scaling_factor = self.cfg_ana.detector.jet_energy_correction(jet)
            jet_rescaled = copy.deepcopy(jet)
            jet_rescaled._tlv *= scaling_factor
            jets_rescaled.append(jet_rescaled)
        setattr(event, self.cfg_ana.output, jets_rescaled)
