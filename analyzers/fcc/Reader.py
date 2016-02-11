from heppy.framework.analyzer import Analyzer
from heppy.particles.fcc.particle import Particle
from heppy.particles.fcc.jet import Jet
from heppy.particles.fcc.vertex import Vertex 

import math
import pprint

class FCCReader(Analyzer):

    def beginLoop(self, setup):
        super(FCCReader, self).beginLoop(setup)
        self.sort_key = lambda ptc: ptc.e()
        if self.cfg_ana.mode=='pp' or self.cfg_ana.mode=='ep':
            self.sort_key = lambda ptc: ptc.pt()
    
    def process(self, event):
        store = event.input
        if hasattr(self.cfg_ana, 'gen_particles'):
            name_genptc = self.cfg_ana.gen_particles
            gen_particles = map(Particle, store.get("GenParticle"))
            event.gen_particles = sorted( gen_particles,
                                          key = self.sort_key,
                                          reverse=True )  
            event.gen_particles_stable = [ptc for ptc in event.gen_particles
                                          if ptc.status()==1 and 
                                          not math.isnan(ptc.e()) and
                                          ptc.e()>1e-5 and 
                                          ptc.pt()>1e-5 and
                                          not abs(ptc.pdgid()) in [12, 14, 16]]
            gen_vertices = store.get("GenVertex")
            event.gen_vertices = map(Vertex, gen_vertices)
        if hasattr(self.cfg_ana, 'gen_jets'):
            event.gen_jets = map(Jet, store.get(self.cfg_ana.gen_jets))
            event.gen_jets.sort(key = self.sort_key, reverse=True)
