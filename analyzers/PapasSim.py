from heppy.framework.analyzer import Analyzer
from heppy.papas.papas_exceptions import PropagationError, SimulationError
from heppy.papas.data.papasevent import PapasEvent
from heppy.papas.simulator import Simulator
from heppy.display.core import Display
from heppy.display.geometry import GDetector
from heppy.papas.data.identifier import Identifier
from heppy.papas.graphtools.DAG import Node
from heppy.papas.pfalgo.distance import Distance
from heppy.papas.mergedclusterbuilder import MergedClusterBuilder


#todo following Alices merge and reconstruction work
# - add muons and electrons back into the particles, these
#   particles are not yet handled by alices reconstruction
#   they are (for the time being) excluded from the simulation rec particles in order that particle
#   comparisons can be made (eg # no of particles)

#todo redo comments once naming and passing arguments have been agreed

class PapasSim(Analyzer):
    '''Runs PAPAS, the PArametrized Particle Simulation.
    
    #This will need to redocumented once new papasevent structure arrives

    Example configuration:

    from heppy.analyzers.PapasSim import PapasSim
    from heppy.papas.detectors.CMS import CMS
    papas = cfg.Analyzer(
        PapasSim,
        instance_label = 'papas',
        detector = CMS(),
        gen_particles = 'gen_particles_stable',
        sim_particles = 'sim_particles',
        merged_ecals = 'ecal_clusters',
        merged_hcals = 'hcal_clusters',
        tracks = 'tracks',
        #rec_particles = 'sim_rec_particles', # optional - will only do a simulation reconstruction if a name is provided
        output_history = 'history_nodes',
        display_filter_func = lambda ptc: ptc.e()>1.,
        display = False,
        verbose = True
    )
    detector:      Detector model to be used.
    gen_particles: Name of the input gen particle collection
    sim_particles: Name extension for the output sim particle collection.
                   Note that the instance label is prepended to this name.
                   Therefore, in this particular case, the name of the output
                   sim particle collection is "papas_sim_particles".
    merged_ecals: Name for the merged clusters created by simulator
    merged_hcals: Name for the merged clusters created by simulator
    tracks:       Name for smeared tracks created by simulator
    rec_particles: Optional. Name extension for the reconstructed particles created by simulator
                   This is retained for the time being to allow two reconstructions to be compared
                   Reconstruction will occur if this parameter  or rec_particles_no_leptons is provided
                   Same comments as for the sim_particles parameter above.
    rec_particles_no_leptons: Optional. Name extension for the reconstructed particles created by simulator
                   without electrons and muons
                   Reconstruction will occur if this parameter  or rec_particles is provided
                   This is retained for the time being to allow two reconstructions to be compared
                   Same comments as for the sim_particles parameter above.
    smeared: Name for smeared leptons
    history: Optional name for the history nodes, set to None if not needed
    display      : Enable the event display
    verbose      : Enable the detailed printout.

        event must contain
          todo once history is implemented
        event will gain
          ecal_clusters:- smeared merged clusters from simulation
          hcal_clusters:- smeared merged clusters from simulation
          tracks:       - tracks from simulation
          baseline_particles:- simulated particles (excluding electrons and muons)
          sim_particles - simulated particles including electrons and muons
        
    '''

    def __init__(self, *args, **kwargs):
        super(PapasSim, self).__init__(*args, **kwargs)
        self.detector = self.cfg_ana.detector
        self.simulator = Simulator(self.detector, self.mainLogger)
        
        self.simname = '_'.join([self.instance_label,  self.cfg_ana.sim_particles])
        #self.is_display = self.cfg_ana.display
        #if self.is_display:
            #self.init_display()

    def init_display(self):
        self.display = Display(['xy', 'yz'])
        self.gdetector = GDetector(self.detector)
        self.display.register(self.gdetector, layer=0, clearable=False)
        self.is_display = True

    def process(self, event):
        
        papasevent = PapasEvent()
        Identifier.reset()
        setattr(event, "papasevent", papasevent)
        setattr(event, "detector", self.detector)
        #if self.is_display:
        #    self.display.clear()
        pfsim_particles = []
        gen_particles = getattr(event, self.cfg_ana.gen_particles)
        
        try:
            self.simulator.simulate(gen_particles)
        except (PropagationError, SimulationError) as err:
            self.mainLogger.error(str(err) + ' -> Event discarded')
            return False
        pfsim_particles = self.simulator.ptcs
            
        simparticles = sorted( pfsim_particles,
                               key = lambda ptc: ptc.e(), reverse=True)     
        setattr(event, self.simname, simparticles)
    
        #create dicts of clusters, particles etc (todo?:move a lot of this into simulator)
        self.build_collections_and_history(papasevent, simparticles)
        
        #todo move to separate analyzer
        self.merge_clusters(papasevent) #add to simulator class? 
        
        papasevent.iEv = event.iEv
    
    def build_collections_and_history(self, papasevent, sim_particles):  
        #this should be integrated into the simulator in the future
        simulated_particles = dict()
        gen_stable_particles = dict()
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
            id = ptc.uniqueid
            simulated_particles[id] = ptc
            history[id] = Node(id)
            gen_id = ptc.gen_ptc.uniqueid
            gen_stable_particles[gen_id] = ptc.gen_ptc
            history[gen_id] = Node(gen_id)
            history[gen_id].add_child(history[id])
    
            if ptc.track:
                track_id = ptc.track.uniqueid
                true_tracks[track_id] = ptc.track
                history[track_id] = Node(track_id)
                history[id].add_child(history[track_id])
                if ptc.track_smeared:
                    smtrack_id = ptc.track_smeared.uniqueid
                    smeared_tracks[smtrack_id] = ptc.track_smeared
                    history[smtrack_id] = Node(smtrack_id)
                    history[track_id].add_child(history[smtrack_id])    
            if len(ptc.clusters) > 0 :   
                for key, clust in ptc.clusters.iteritems():
                    if key=="ecal_in" :  #todo check this .or. key=="ecal_decay" :
                        true_ecals[clust.uniqueid] = clust                       
                    elif key=="hcal_in" :
                        true_hcals[clust.uniqueid] = clust
                    else:
                        assert false                    
                    history[clust.uniqueid] = Node(clust.uniqueid)
                    history[id].add_child(history[clust.uniqueid])  
    
            if len(ptc.clusters_smeared) > 0 :   
                for key1, smclust in ptc.clusters_smeared.iteritems():
                    if (key ==key1): 
                        if key=="ecal_in" :  #todo check this .or. key=="ecal_decay" :
                            smeared_ecals[smclust.uniqueid]=smclust
                        elif key=="hcal_in" :
                            smeared_hcals[smclust.uniqueid]=smclust 
                        history[smclust.uniqueid] = Node(smclust.uniqueid)
                        history[clust.uniqueid].add_child(history[smclust.uniqueid])
                            
        papasevent.add_collection(simulated_particles)
        papasevent.add_collection(gen_stable_particles)
        papasevent.add_collection(true_tracks)
        papasevent.add_collection(smeared_tracks)
        papasevent.add_collection(smeared_hcals)
        papasevent.add_collection(true_hcals)
        papasevent.add_collection(smeared_ecals)
        papasevent.add_collection(true_ecals)    
            

    def merge_clusters(self, papasevent): # todo move to a separate analyzer
               #Now merge the simulated clusters as a separate pre-stage (prior to new reconstruction)        
        ruler = Distance()
        merged_ecals = MergedClusterBuilder(papasevent.get_collection('es'), ruler, papasevent.history).merged
        merged_hcals = MergedClusterBuilder(papasevent.get_collection('hs'), ruler, papasevent.history).merged
        papasevent.add_collection(merged_ecals)
        papasevent.add_collection(merged_hcals)
