from heppy.framework.analyzer import Analyzer
from heppy.particles.fcc.particle import Particle 

import math
from heppy.papas.simulator import Simulator
from heppy.papas.papas_exceptions import PropagationError
from heppy.papas.vectors import Point
from heppy.papas.pfobjects import Particle as PFSimParticle
from heppy.papas.toyevents import particles
from heppy.display.core import Display
from heppy.display.geometry import GDetector
from heppy.display.pfobjects import GTrajectories

from ROOT import TLorentzVector, TVector3

        
class Papas(Analyzer):
    '''Runs PAPAS, the PArametrized Particle Simulation. 

    Papas reads a list of stable generated particles, 
    and creates a list of reconstruted particles. 
    First, the particles are extrapolated in the magnetic field
    through the tracker and to the calorimeters, 
    and the particle deposits are simulated using a parametrized simulation. 
    Then, a particle flow algorithm is used to connect the simulated tracks 
    and calorimeter energy deposits, and to identify and reconstruct 
    final state particles. 

    Example: 

    from heppy.analyzers.Papas import Papas
    from heppy.papas.detectors.CMS import CMS
    papas = cfg.Analyzer(
      Papas,
      instance_label = 'papas',
      detector = CMS(),
      gen_particles = 'gen_particles_stable',
      sim_particles = 'sim_particles',
      rec_particles = 'particles',
      display = False,
      verbose = True
    )

    detector:      Detector model to be used, here CMS.  
    gen_particles: Name of the input gen particle collection
    sim_particles: Name for the output sim particle collection. 
    rec_particles: Name for the output reconstructed particle collection.
    display      : Enable the event display
    verbose      : Enable the detailed printout.
    '''

    def __init__(self, *args, **kwargs):
        super(Papas, self).__init__(*args, **kwargs)
        self.detector = self.cfg_ana.detector
        self.simulator = Simulator(self.detector,
                                   self.mainLogger)
        self.is_display = self.cfg_ana.display
        if self.is_display:
            self.init_display()        
        
    def init_display(self):
        self.display = Display(['xy','yz'])
        self.gdetector = GDetector(self.detector)
        self.display.register(self.gdetector, layer=0, clearable=False)
        self.is_display = True
        
    def process(self, event):
        event.simulator = self 
        if self.is_display:
            self.display.clear()
        pfsim_particles = []
        gen_particles = getattr(event, self.cfg_ana.gen_particles)
        try: 
            self.simulator.simulate( gen_particles )
        except PropagationError as err:
            self.mainLogger.error( str(err) + ' -> Event discarded')
            return False
        pfsim_particles = self.simulator.ptcs
        if self.is_display:
            particles_for_display = pfsim_particles
            if hasattr(self.cfg_ana, 'display_filter_func'):
                particles_for_display = [ ptc for ptc in pfsim_particles if 
                                          self.cfg_ana.display_filter_func(ptc) ]
            self.display.register( GTrajectories(particles_for_display),
                                   layer=1)
        simparticles = sorted( pfsim_particles,
                               key = lambda ptc: ptc.e(), reverse=True)
        particles = sorted( self.simulator.particles,
                            key = lambda ptc: ptc.e(), reverse=True)
        setattr(event, self.cfg_ana.sim_particles, simparticles)
        setattr(event, self.cfg_ana.rec_particles, particles)
