from heppy.framework.analyzer import Analyzer
from heppy.particles.isolation import EtaPhiCircle
from heppy.particles.tlv.particle import Particle
from ROOT import TLorentzVector
import pprint 

class LeptonFsrDresser(Analyzer):
    '''Dresses input lepton collection with another collection. Can be used for dressing leptons with FSR photons for instance. 

    Example:

    from heppy.analyzers.Dresser import Dresser
    from heppy.particles.isolation import EtaPhiCircle
    
    dressed_leptons = cfg.Analyzer(
    LeptonFsrDresser,
      leptons = 'leptons',
      particles = 'photons',
      output = 'dressed_leptons'
      area = EtaPhiCircle(0.3)
    )
    
    * leptons : collection of leptons to be dressed

    * particles : collection of particles to dress leptons with 

    * output : name of the output collection 

    * area : size of the cone where particles can be counted for dressing
    '''
    
    def process(self, event):
        particles = getattr(event, self.cfg_ana.particles)
        leptons = getattr(event, self.cfg_ana.leptons)
        
        dressed = []
        for lepton in leptons:
            sump4 = TLorentzVector()
             
            for particle in particles:
                if self.cfg_ana.area.is_inside(lepton.eta(), lepton.phi(),
                                  particle.eta(), particle.phi() ):
                    sump4 += particle.p4()

            sump4 += lepton.p4()
            dressed.append( Particle(lepton.pdgid(), lepton.q(), sump4) )
        
        setattr(event, self.cfg_ana.output, dressed)

