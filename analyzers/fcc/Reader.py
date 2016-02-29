from heppy.framework.analyzer import Analyzer
from heppy.particles.fcc.particle import Particle
from heppy.particles.fcc.jet import Jet
from heppy.particles.fcc.vertex import Vertex 

import math

class Reader(Analyzer):
    '''Reads events in FCC EDM format, and creates lists of objects adapted to an
    analysis in python.

    Configuration: 
    ----------------------
    
    Example: 
    
    from heppy.analyzers.fcc.Reader import Reader
    source = cfg.Analyzer(
      Reader,
      mode = 'ee',
      # all the parameters below are optional: 
      gen_particles = 'GenParticle',
      # gen_vertices = '<gen_vertices_name>', 
      # gen_jets = '<gen_jets_name>',
      # jets = '<jets_name>',
    )

    * mode: 

    'ee', 'pp', or 'ep'.

    In 'ee' mode, particle-like objects are sorted by decreasing energy. 
    in other modes, by decreasing pt.

    * gen_particles: 

    Name of the collection of gen particles in the input 
    root file. Open the root file with root, and print the events TTree 
    to see which collections are present in your input file.

    Creates: 
    --------    

    if self.cfg_ana.gen_particles is set: 
    - event.gen_particles: gen particles
    - event.gen_particles_stable: stable gen_particles except neutrinos

    if the respective parameter is set (see above): 
    - event.gen_vertices: gen vertices (needed for gen particle history)
    - event.gen_jets: gen jets
    - event.jets: reconstructed jets  
    '''

    def beginLoop(self, setup):
        super(Reader, self).beginLoop(setup)
        self.sort_key = lambda ptc: ptc.e()
        if self.cfg_ana.mode=='pp' or self.cfg_ana.mode=='ep':
            self.sort_key = lambda ptc: ptc.pt()
    
    def process(self, event):
        store = event.input
        if hasattr(self.cfg_ana, 'gen_particles'):
            name_genptc = self.cfg_ana.gen_particles
            gen_particles = map(Particle, store.get(self.cfg_ana.gen_particles))
            event.gen_particles = sorted( gen_particles,
                                          key = self.sort_key,
                                          reverse=True )
            event.gen_particles_stable = [ptc for ptc in event.gen_particles
                                          if ptc.status()==1 and 
                                          not math.isnan(ptc.e()) and
                                          ptc.e()>1e-5 and 
                                          ptc.pt()>1e-5 and
                                          not abs(ptc.pdgid()) in [12, 14, 16]]
        if hasattr(self.cfg_ana, 'gen_vertices'):        
            gen_vertices = store.get(self.cfg_ana.gen_vertices)
            event.gen_vertices = map(Vertex, gen_vertices)
        if hasattr(self.cfg_ana, 'gen_jets'):
            event.gen_jets = map(Jet, store.get(self.cfg_ana.gen_jets))
            event.gen_jets.sort(key = self.sort_key, reverse=True)
        if hasattr(self.cfg_ana, 'jets'):
            event.jets = map(Jet, store.get(self.cfg_ana.jets))
            event.jets.sort(key = self.sort_key, reverse=True)
        
        
            
