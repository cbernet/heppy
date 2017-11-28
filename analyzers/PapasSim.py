from heppy.framework.analyzer import Analyzer
from heppy.papas.pfobjects import Particle 
from heppy.papas.papas_exceptions import PropagationError, SimulationError
from heppy.papas.data.papasevent import PapasEvent
from heppy.papas.simulator import Simulator
from heppy.papas.data.idcoder import IdCoder
from heppy.papas.graphtools.DAG import Node
from heppy.papas.pfalgo.distance import Distance
from heppy.papas.mergedclusterbuilder import MergedClusterBuilder
from heppy.particles.p4 import P4
from heppy.utils.pdebug import pdebugger
import heppy.statistics.rrandom as random

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
        verbose = True
    )
    detector:      Detector model to be used.
    gen_particles: Name of the input gen particle collection
    sim_particles: Name extension for the output sim particle collection.
                   Note that the instance label is prepended to this name.
                   Therefore, in this particular case, the name of the output
                   sim particle collection is "papas_sim_particles".
    verbose      : Enable the detailed printout.

        event must contain
          gen_particles
        event will gain
          papasevent - simulated objects (simulated particles, tracks, and clusters) and history
          simparticles - simulated particles of the papasevent, as a list. 
    '''

    def __init__(self, *args, **kwargs):
        super(PapasSim, self).__init__(*args, **kwargs)
        self.simulator = Simulator(self.cfg_ana.detector, self.mainLogger)
        self.simname = '_'.join([self.instance_label,  self.cfg_ana.sim_particles])

    def process(self, event):
        #random.seed(0xdeadbeef) #Useful to make results reproducable between loops and single runs
        event.simulator = self
        event.papasevent = PapasEvent(event.iEv)   
        papasevent = event.papasevent
        gen_particles = getattr(event, self.cfg_ana.gen_particles)
        gen_particles_collection = {} #make a dict from the gen_particles list so that it can be stored into the papasevent collections  
        for g in gen_particles:
            g.set_dagid(IdCoder.make_id(IdCoder.PFOBJECTTYPE.PARTICLE, g.objid()[0], 'g', g.p4().E()))
            gen_particles_collection[g.dagid()] = g
        def simparticle(ptc, index):
            '''Create a sim particle to be used in papas from an input particle.
            '''
            tp4 = ptc.p4()
            vertex = ptc.start_vertex().position()
            charge = ptc.q()
            pid = ptc.pdgid()
            simptc = Particle(tp4, vertex, charge, pid)
            simptc.set_dagid(IdCoder.make_id(IdCoder.PFOBJECTTYPE.PARTICLE, index, 's', simptc.idvalue))
            pdebugger.info(" ".join(("Made", simptc.__str__())))
            #simptc.gen_ptc = ptc
            #record that sim particle derives from gen particle
            child = papasevent.history.setdefault(simptc.dagid(), Node(simptc.dagid())) #creates a new node if it is not there already
            parent = papasevent.history.setdefault(ptc.dagid(), Node(ptc.dagid()))
            parent.add_child(child)
            return simptc
        simptcs = [simparticle(ptc, index)
                   for index, ptc in enumerate(gen_particles)]
        try:
            self.simulator.simulate(simptcs, papasevent.history)
        except (PropagationError, SimulationError) as err:
            self.mainLogger.error(str(err) + ' -> Event discarded')
            return False
        #these are the particles before simulation
        simparticles = sorted(self.simulator.ptcs, key=P4.sort_key, reverse=True)
        setattr(event, self.simname, simparticles)
        papasevent.add_collection(gen_particles_collection)
        papasevent.add_collection(self.simulator.simulated_particles)
        papasevent.add_collection(self.simulator.true_tracks)
        papasevent.add_collection(self.simulator.smeared_tracks)
        papasevent.add_collection(self.simulator.smeared_hcals)
        papasevent.add_collection(self.simulator.true_hcals)
        papasevent.add_collection(self.simulator.smeared_ecals)
        papasevent.add_collection(self.simulator.true_ecals)  

        #todo move to separate analyzer
        self.merge_clusters(papasevent) #add to simulator class? 
        #useful when producing outputs from a papasevent
        papasevent.iEv = event.iEv
            

    def merge_clusters(self, papasevent): # todo move to a separate analyzer
        #For Now merge the simulated clusters as a separate pre-stage (prior to new reconstruction)        
        ruler = Distance()
        merged_ecals = dict()
        merged_hcals = dict()
        ecals = papasevent.get_collection('es')
        if ecals:
            merged_ecals = MergedClusterBuilder(papasevent.get_collection('es'), ruler, papasevent.history).merged_clusters
        hcals = papasevent.get_collection('hs')
        if hcals:        
            merged_hcals = MergedClusterBuilder(papasevent.get_collection('hs'), ruler, papasevent.history).merged_clusters
        papasevent.add_collection(merged_ecals)
        papasevent.add_collection(merged_hcals)
