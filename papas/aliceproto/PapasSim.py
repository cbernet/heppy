from heppy.framework.analyzer import Analyzer
from heppy.particles.fcc.particle import Particle 

import math
from heppy.papas.simulator import Simulator
from heppy.papas.vectors import Point
from heppy.papas.pfobjects import Particle as PFSimParticle
from heppy.papas.toyevents import particles
from heppy.display.core import Display
from heppy.display.geometry import GDetector
from heppy.display.pfobjects import GTrajectories
from heppy.papas.pfalgo.distance  import Distance

from heppy.papas.pfalgo.pfinput import PFInput
from heppy.papas.aliceproto.mergingblockbuilder import MergingBlockBuilder
from heppy.papas.aliceproto.comparer import ClusterComparer, TrackComparer
from heppy.papas.aliceproto.pfevent import PFEvent
from ROOT import TLorentzVector, TVector3


class PapasSim(Analyzer):
    '''Runs PAPAS, the PArametrized Particle Simulation.

    Example configuration: 

    from heppy.analyzers.PapasSim import PapasSim
    from heppy.papas.detectors.CMS import CMS
    papas = cfg.Analyzer(
        PapasSim,
        instance_label = 'papas',              
        detector = CMS(),
        gen_particles = 'gen_particles_stable',
        sim_particles = 'sim_particles',
        rec_particles = 'rec_particles',
        display = False,                   
        verbose = False
    )

    detector:      Detector model to be used. 
    gen_particles: Name of the input gen particle collection
    sim_particles: Name extension for the output sim particle collection. 
                   Note that the instance label is prepended to this name. 
                   Therefore, in this particular case, the name of the output 
                   sim particle collection is "papas_sim_particles".
    rec_particles: Name extension for the output reconstructed particle collection.
                   Same comments as for the sim_particles parameter above. 
    display      : Enable the event display
    verbose      : Enable the detailed printout.
    '''

    def __init__(self, *args, **kwargs):
        super(PapasSim, self).__init__(*args, **kwargs)
        self.detector = self.cfg_ana.detector
        self.simulator = Simulator(self.detector,
                                   self.mainLogger)
        self.simname = '_'.join([self.instance_label,  self.cfg_ana.sim_particles])
        self.recname = '_'.join([self.instance_label,  self.cfg_ana.rec_particles])
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
        self.simulator.simulate( gen_particles )
        pfsim_particles = self.simulator.ptcs
        if self.is_display:
            self.display.register( GTrajectories(pfsim_particles),
                                   layer=1)
        simparticles = sorted( pfsim_particles,
                               key = lambda ptc: ptc.e(), reverse=True)
        particles = sorted( self.simulator.particles,
                            key = lambda ptc: ptc.e(), reverse=True)
        #excludes muons and electrons         
        origrecparticles = sorted( self.simulator.pfsequence.pfreco.particles,
                                   key = lambda ptc: ptc.e(), reverse=True)
        setattr(event, "orig_rec_particles",origrecparticles)
        
        
        #here we merge the simulated clusters and tracks as a separate pre-stage (prior to reconstruction)
        event.tracks = dict()
        event.ecal_clusters = dict()
        event.hcal_clusters = dict() 
        if "tracker" in self.simulator.pfsequence.pfinput.elements :
            for element in self.simulator.pfsequence.pfinput.elements["tracker"]:
                event.tracks[element.uniqueid] = element 
        if "ecal_in" in self.simulator.pfsequence.pfinput.elements :        
            for element in self.simulator.pfsequence.pfinput.elements["ecal_in"]:
                event.ecal_clusters[element.uniqueid] = element 
        if "hcal_in" in self.simulator.pfsequence.pfinput.elements :
            for element in self.simulator.pfsequence.pfinput.elements["hcal_in"]:
                event.hcal_clusters[element.uniqueid] = element 
        ruler = Distance()
        #event.tracks = MergingBlockBuilder("tracker",PFEvent(event), ruler).merged
        event.ecal_clusters =  MergingBlockBuilder("ecal_in",PFEvent(event), ruler).merged
        event.hcal_clusters = MergingBlockBuilder("hcal_in",PFEvent(event), ruler).merged  
        event.testtracks =event.tracks
        event.testecal_clusters =  event.ecal_clusters
        event.testhcal_clusters = event.hcal_clusters          
        
        #for blockbuilder to get merged clusters and to compare with the non-electron etc by passed particles
        setattr(event,self.simname,simparticles) #check
        event.baseline_particles = origrecparticles
        event.sim_partciles = simparticles        
        
        #for now we use the original reconstructions to provide the ready merged tracks and clusters
        event.tracks = dict()
        event.ecal_clusters = dict()
        event.hcal_clusters = dict()
        for element in self.simulator.pfsequence.elements :
            if element.__class__.__name__ == 'SmearedTrack': 
                event.tracks[element.uniqueid] = element 
            elif element.__class__.__name__ == 'SmearedCluster' and element.layer == 'ecal_in': 
                event.ecal_clusters[element.uniqueid] = element
            elif element.__class__.__name__ == 'SmearedCluster' and element.layer == 'hcal_in': 
                event.hcal_clusters[element.uniqueid] = element
            else :            
                print element.__class__.__name__ 
                assert(False)
         
        #compare old and new cluster methods 
        ClusterComparer(event.testecal_clusters,event.ecal_clusters)
        ClusterComparer(event.testhcal_clusters,event.hcal_clusters)
       
        pass

        
