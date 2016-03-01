from heppy.framework.analyzer import Analyzer
from heppy.particles.fcc.particle import Particle
from heppy.particles.fcc.jet import Jet
from heppy.particles.fcc.vertex import Vertex 
from heppy.particles.fcc.met import Met

import math
import pprint

class Reader(Analyzer):

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

            jets = dict()
            for jet in event.jets: 
                jets[Jet(jet.fccjet)] = jet
            print jets

            if hasattr(self.cfg_ana, 'bTags') and hasattr(self.cfg_ana, 'jetsToBTags'):
                for tt in store.get(self.cfg_ana.jetsToBTags):
                    print jets[tt.Jet()]
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
            
