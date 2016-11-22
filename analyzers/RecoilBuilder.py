'''Computes the 4 momentum recoiling agains a selection of particles.'''

from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.particle import Particle as Recoil

from ROOT import TLorentzVector

mass = {23: 91, 25: 125}

class RecoilBuilder(Analyzer):
    '''Computes the 4 momentum recoiling agains a selection of particles.
    
    Example:: 
        from heppy.analyzers.RecoilBuilder import RecoilBuilder
        recoil = cfg.Analyzer(
          RecoilBuilder,
          output = 'recoil',
          sqrts = 240.,
          to_remove = 'zeds_legs'
        ) 

    @param output: the recoiling L{particle<heppy.particles.tlv.particle>} is stored in this collection
    
    @param sqrts: centre-of-mass energy, used to compute the initial-state p4
    
    @param to_remove : collection of particles to be subtracted to the initial-state p4.
      if to_remove is set to the whole collection of reconstructed particles
      in the event, the missing p4 is computed (missing energy).

    '''
    
    def process(self, event):
        '''Process the event.
        
        The event must contain:
         - self.cfg_ana.to_remove: the collection of particles against which the system recoils.
         
        This method creates:
         - event.<self.cfg_ana.output> : the recoiling L{particle<heppy.particles.tlv.particle>}.
        '''
        sqrts = self.cfg_ana.sqrts
        to_remove = getattr(event, self.cfg_ana.to_remove) 
        recoil_p4 = TLorentzVector(0, 0, 0, sqrts)
        for ptc in to_remove:
            recoil_p4 -= ptc.p4()
        recoil = Recoil(0, 0, recoil_p4, 1) 
        setattr(event, self.cfg_ana.output, recoil)
                
