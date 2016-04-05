from heppy.framework.analyzer import Analyzer
from heppy.particles.fcc.particle import Particle
from heppy.particles.fcc.jet import Jet
from heppy.particles.fcc.vertex import Vertex 
from heppy.particles.fcc.met import Met

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
            #import pdb; pdb.set_trace()
            gen_particles = map(Particle, store.get(self.cfg_ana.gen_particles))
            event.gen_particles = sorted( gen_particles,
                                          key = self.sort_key,
                                          reverse=True )
            # event.gen_particles_stable = [ptc for ptc in event.gen_particles
            #                               if ptc.status()==1 and 
            #                               not math.isnan(ptc.e()) and
            #                               ptc.e()>1e-5 and 
            #                               ptc.pt()>1e-5 and
            #                               not abs(ptc.pdgid()) in [12, 14, 16]]
        if hasattr(self.cfg_ana, 'gen_vertices'):        
            gen_vertices = store.get(self.cfg_ana.gen_vertices)
            event.gen_vertices = map(Vertex, gen_vertices)
 
        if hasattr(self.cfg_ana, 'gen_jets'):
            event.gen_jets = map(Jet, store.get(self.cfg_ana.gen_jets))
            event.gen_jets.sort(key = self.sort_key, reverse=True)

        jets = dict()
        if hasattr(self.cfg_ana, 'jets'):
            event.jets = map(Jet, store.get(self.cfg_ana.jets))
            event.jets.sort(key = self.sort_key, reverse=True) 
            for jet in event.jets: 
                jets[jet] = jet

        if hasattr(self.cfg_ana, 'bTags') and hasattr(self.cfg_ana, 'jetsToBTags'):
            for tt in store.get(self.cfg_ana.jetsToBTags):
                jets[Jet(tt.Jet())].tags['bf'] = tt.Tag().Value()
                # do this in your btag module:
                jets[Jet(tt.Jet())].tags['b'] = tt.Tag().Value()>0.
                
                #print '  =====  ',tt.Jet  
                #print jet.pt(),'  ',math.sqrt(tt.Jet().Core().P4.Px**2+tt.Jet().Core().P4.Py**2)
#                    #jet.btag = 0
#
#                print '----------------------------   ',store.get(self.cfg_ana.jetsToBTags)
#                for tt in store.get(self.cfg_ana.jetsToBTags):
#                    print 'jet ',tt.Jet().Core().P4.Px
#                    print 'tag ',tt.Tag().Value()
  


        class Iso(object):
            def __init__(self):
                self.sumpt=1
                self.sume=2
                self.num=3

        if hasattr(self.cfg_ana, 'electrons'):
            event.electrons = map(Particle, store.get(self.cfg_ana.electrons))
            event.electrons.sort(key = self.sort_key, reverse=True)
            for ele in event.electrons:
                ele.iso = Iso()

        if hasattr(self.cfg_ana, 'muons'):
            event.muons = map(Particle, store.get(self.cfg_ana.muons))
            event.muons.sort(key = self.sort_key, reverse=True)   
            for mu in event.muons:
                mu.iso = Iso()

        if hasattr(self.cfg_ana, 'photons'):
            event.photons = map(Particle, store.get(self.cfg_ana.photons))
            event.photons.sort(key = self.sort_key, reverse=True)   

        if hasattr(self.cfg_ana, 'met'):
            event.met = map(Met, store.get(self.cfg_ana.met))[0]
            
