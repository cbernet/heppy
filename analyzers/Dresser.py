from heppy.framework.analyzer import Analyzer
from heppy.particles.isolation import EtaPhiCircle
from heppy.particles.tlv.particle import Particle
from ROOT import TLorentzVector
import pprint 

class Dresser(Analyzer):
    '''Dresses input collection with other collection. Can be used for dressing leptons with FSR photons for instance. 

    Example:

    from heppy.analyzers.Dresser import Dresser
    from heppy.particles.isolation import EtaPhiCircle
    
    dressed_leptons = cfg.Analyzer(
    Dresser,
      candidates = 'leptons',
      particles = 'photons',
      output = 'dressed_leptons'
      area = EtaPhiCircle(0.3)
    )
    
    * candidates : collection of candidates for to be dressed

    * particles : collection of particles to dress candidates with 

    '''
    def process(self, event):
        particles = getattr(event, self.cfg_ana.particles)
        candidates = getattr(event, self.cfg_ana.candidates)
       
        dressed = []
	for candidate in candidates:
#	    print 'dressed before: ', candidate
	    
	    sump4 = TLorentzVector()
	     
	    for particle in particles:
	        if self.cfg_ana.area.is_inside(candidate.eta(), candidate.phi(),
                                  particle.eta(), particle.phi() ):
#                    print 'fsr photon' , particle, particle.iso.sumpt/particle.pt()
		
		    sump4 += particle.p4()
	
	    sump4 += candidate.p4()     	           
	    dressed.append( Particle(candidate.pdgid(), candidate.q(), sump4) )
	
#	    print 'dressed after: ', Particle(candidate.pdgid(), candidate.q(), sump4)
	
	setattr(event, self.cfg_ana.output, dressed)    
	   
