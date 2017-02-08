from heppy.framework.analyzer import Analyzer
from heppy.papas.papas_exceptions import PropagationError, SimulationError
from heppy.papas.data.papasevent import PapasEvent
from heppy.papas.simulator import Simulator
from heppy.papas.data.identifier import Identifier
from heppy.papas.graphtools.DAG import Node
from heppy.papas.pfalgo.distance import Distance
from heppy.papas.mergedclusterbuilder import MergedClusterBuilder
from heppy.particles.p4 import P4

import heppy.statistics.rrandom as random

#todo following Alices merge and reconstruction work
# - add muons and electrons back into the particles, these
#   particles are not yet handled by alices reconstruction
#   they are (for the time being) excluded from the simulation rec particles in order that particle
#   comparisons can be made (eg # no of particles)

#todo redo comments once naming and passing arguments have been agreed

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
        papasevent = PapasEvent(event.iEv)
        self.particles = dict()
        #self.splitblocks = dict()
        #blocks = papasevent.get_collection(block_type_and_subtype)           
        setattr(event, "papasevent", papasevent)        
        pfsim_particles = []
        gen_particles = getattr(event, self.cfg_ana.gen_particles)
        try:
            self.simulator.simulate(gen_particles)
        except (PropagationError, SimulationError) as err:
            self.mainLogger.error(str(err) + ' -> Event discarded')
            return False
        pfsim_particles = self.simulator.ptcs

        #these are the particles before simulation
        simparticles = sorted(pfsim_particles, key=P4.sort_key)

        setattr(event, self.simname, simparticles)
    
        #create dicts of clusters, particles etc (todo?:move a lot of this into simulator)
        self.build_collections_and_history(papasevent, simparticles)
        
        #todo move to separate analyzer
        self.merge_clusters(papasevent) #add to simulator class? 
        #useful when producing outputs from a papasevent
        papasevent.iEv = event.iEv
    
    def build_collections_and_history(self, papasevent, sim_particles):  
        #todo this should be integrated into the simulator in the future
        simulated_particles = dict()
        tracks = dict()
        smeared_tracks=dict()
        smeared_hcals = dict()
        true_hcals = dict()
        smeared_ecals = dict()
        true_ecals = dict()    
        smeared_tracks = dict()
        true_tracks = dict()            
        
        history =  papasevent.history
        for ptc in sim_particles:
            uid = ptc.uniqueid
            simulated_particles[uid] = ptc
            history[uid] = Node(uid)
            if ptc.track:
                track_id = ptc.track.uniqueid
                true_tracks[track_id] = ptc.track
                history[track_id] = Node(track_id)
                history[uid].add_child(history[track_id])
                if ptc.track_smeared:
                    smtrack_id = ptc.track_smeared.uniqueid
                    smeared_tracks[smtrack_id] = ptc.track_smeared
                    history[smtrack_id] = Node(smtrack_id)
                    history[track_id].add_child(history[smtrack_id])    
            if len(ptc.clusters) > 0 : 
                for key, clust in ptc.clusters.iteritems():
                    if Identifier.get_type(clust.uniqueid) == Identifier.PFOBJECTTYPE.ECALCLUSTER:
                        true_ecals[clust.uniqueid] = clust                       
                    elif Identifier.get_type(clust.uniqueid) == Identifier.PFOBJECTTYPE.HCALCLUSTER:
                        true_hcals[clust.uniqueid] = clust
                    else:
                        assert(False)                    
                    history[clust.uniqueid] = Node(clust.uniqueid)
                    history[uid].add_child(history[clust.uniqueid])  
    
                    if len(ptc.clusters_smeared) > 0 :  #need to put in link between true and smeared cluster 
                        for key1, smclust in ptc.clusters_smeared.iteritems():
                            if (key == key1): 
                                if Identifier.get_type(smclust.uniqueid) == Identifier.PFOBJECTTYPE.ECALCLUSTER:
                                    smeared_ecals[smclust.uniqueid]=smclust
                                elif Identifier.get_type(smclust.uniqueid) == Identifier.PFOBJECTTYPE.HCALCLUSTER:
                                    smeared_hcals[smclust.uniqueid]=smclust 
                                history[smclust.uniqueid] = Node(smclust.uniqueid)
                                history[clust.uniqueid].add_child(history[smclust.uniqueid])
                            
        papasevent.add_collection(simulated_particles)
        papasevent.add_collection(true_tracks)
        papasevent.add_collection(smeared_tracks)
        papasevent.add_collection(smeared_hcals)
        papasevent.add_collection(true_hcals)
        papasevent.add_collection(smeared_ecals)
        papasevent.add_collection(true_ecals)    
            

    def merge_clusters(self, papasevent): # todo move to a separate analyzer
        #For Now merge the simulated clusters as a separate pre-stage (prior to new reconstruction)        
        ruler = Distance()
        merged_ecals = dict()
        merged_hcals = dict()
        ecals = papasevent.get_collection('es')
        if ecals:
            merged_ecals = MergedClusterBuilder(papasevent.get_collection('es'), ruler, papasevent.history).merged
        hcals = papasevent.get_collection('hs')
        if hcals:        
            merged_hcals = MergedClusterBuilder(papasevent.get_collection('hs'), ruler, papasevent.history).merged
        papasevent.add_collection(merged_ecals)
        papasevent.add_collection(merged_hcals)
