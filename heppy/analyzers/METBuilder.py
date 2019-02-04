'''Computes the L{MET<heppy.particles.tlv.met.MET>}.'''

from heppy.framework.analyzer import Analyzer

from heppy.particles.tlv.met import MET
from ROOT import TLorentzVector 

class METBuilder(Analyzer):
    '''Computes the L{MET<heppy.particles.tlv.met.MET>}.
    
    Example::
    
        metbuilder = cfg.Analyzer(
           METBuilder,
           instance_label = 'met'
           particles = 'rec_particles'
        )
    
    @param particles: input collection of particles (could be jets to compute MHT).
    @param instance_label: label for a particular instance of the METBuilder.
          used as a name to store in the event the output L{MET<heppy.particles.tlv.met.MET>}.
          
    '''    
    
    def process(self, event):
        '''Process the event.
    
        The event must contain:
         - self.cfg_ana.particles : the input collection of particles
    
        This method creates:
         - event.<self.instance_label> : output L{MET<heppy.particles.tlv.met.MET>}
        '''
        particles = getattr(event, self.cfg_ana.particles)
        missingp4 = TLorentzVector()
        sumpt = 0 
        for ptc in particles:
            missingp4 += ptc.p4()
            sumpt += ptc.pt()
        missingp4 *= -1
        met = MET(missingp4, sumpt)
        setattr(event, self.instance_label, met)
