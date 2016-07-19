from heppy.framework.analyzer import Analyzer
from heppy.particles.fcc.particle import Particle
from heppy.particles.fcc.jet import Jet
from heppy.particles.fcc.vertex import Vertex 
from heppy.particles.fcc.met import Met

import math

class MissingCollection(Exception):
    pass

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
        
        def get_collection(class_object, coll_label, sort=True):
            pycoll = None
            if hasattr(self.cfg_ana, coll_label):
                coll_name = getattr( self.cfg_ana, coll_label)
                coll = store.get( coll_name )
                if coll == None:
                    raise MissingCollection(
                        'collection {} is missing'.format(coll_name)
                        )
                pycoll = map(class_object, coll)
                if sort:
                    pycoll.sort(key = self.sort_key, reverse=True)
                setattr(event, coll_label, pycoll )
            return pycoll

        get_collection(Particle, 'gen_particles')
        get_collection(Vertex, 'gen_vertices', False)
        get_collection(Jet, 'gen_jets')
