'''Computes the total 4 momentum of a selection of particles.'''

from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.particle import Particle
from heppy.particles.tlv.jet import Jet
from heppy.particles.jet import JetConstituents

from ROOT import TLorentzVector

mass = {23: 91, 25: 125}

class SingleJetBuilder(Analyzer):
    '''Builds a (pseudo)-jet with all input particles.
    
    This class is mainly used for papas debugging purpose.
    It allows to check the total p4 of the input particles,
    as well as their flavour. 
    
    Example::
    
        from heppy.analyzers.SingleJetBuilder import SingleJetBuilder
        recoil = cfg.Analyzer(
          SingleJetBuilder,
          particles = 'rec_particles',
          output = 'sum_ptc',
        ) 

    @param particles: collection of input particles.

    @param output: contains a single particle with a p4 equal to the
               sum p4 of all input particles. The single particle is of
               type L{particles.jet.Jet} to keep track of the
               L{jet constituents<particles.jet.JetConstituents>}.
    
    '''
    
    def process(self, event):
        '''Process event.
        
        The event must contain:
         - self.cfg_ana.particles: the input collection of particles.
        '''
        p4 = TLorentzVector()
        charge = 0
        pdgid = 0
        ptcs = getattr(event, self.cfg_ana.particles)
        jet = Jet(p4)
        constituents = JetConstituents()
        for ptc in ptcs:
            p4 += ptc.p4()
            charge += ptc.q()
            constituents.append(ptc)
        sumptc = Particle(pdgid, charge, p4)
        jet = Jet(p4)
        jet.constituents = constituents
        jet.constituents.sort()
        setattr(event, self.cfg_ana.output, jet)
                
