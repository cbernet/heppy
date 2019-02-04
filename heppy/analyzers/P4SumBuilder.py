'''Computes the total 4 momentum of a selection of particles.'''

from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.particle import Particle
from heppy.particles.tlv.jet import Jet
from heppy.particles.jet import JetConstituents

from ROOT import TLorentzVector

mass = {23: 91, 25: 125}

class P4SumBuilder(Analyzer):
    '''Builds the p4 sum of all input particles
    
    Example::
    
        from heppy.analyzers.P4SumBuilder import P4SumBuilder
        sum_vis = cfg.Analyzer(
          P4SumBuilder,
          output = 'sum_vis',
          particles = 'rec_particles',
        ) 

    @param particles: collection of input particles.

    @param output: contains a single particle with a p4 equal to the
               sum p4 of all input particles. The single particle is of
               type L{particles.particle.Particle}.
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
        for ptc in ptcs:
            p4 += ptc.p4()
            charge += ptc.q()
        sumptc = Particle(pdgid, charge, p4)
        setattr(event, self.cfg_ana.output, sumptc)
                
