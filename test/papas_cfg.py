import heppy.framework.config as cfg

# Use a Filter to select stable gen particles for simulation
# from the output of "source" 
# help(Filter) for more information
from heppy.analyzers.Filter import Filter
gen_particles_stable = cfg.Analyzer(
    Filter,
    output = 'gen_particles_stable',
    # output = 'particles',
    input_objects = 'gen_particles',
    filter_func = lambda x : x.status()==1 and abs(x.pdgid()) not in [12,14,16] and x.pt()>1e-5
)

# configure the papas fast simulation with the CMS detector
# help(Papas) for more information
# history nodes keeps track of which particles produced which tracks, clusters 
from heppy.analyzers.PapasSim import PapasSim
# from heppy.analyzers.Papas import Papas
from heppy.papas.detectors.CMS import CMS
detector = CMS()

papas = cfg.Analyzer(
    PapasSim,
    instance_label = 'papas',
    detector = detector,
    gen_particles = 'gen_particles_stable',
    sim_particles = 'sim_particles',
    merged_ecals = 'ecal_clusters',
    merged_hcals = 'hcal_clusters',
    tracks = 'tracks', 
    output_history = 'history_nodes', 
    display_filter_func = lambda ptc: ptc.e()>1.,
    display = False,
    verbose = True
)


# group the clusters, tracks from simulation into connected blocks ready for reconstruction
from heppy.analyzers.PapasPFBlockBuilder import PapasPFBlockBuilder
pfblocks = cfg.Analyzer(
    PapasPFBlockBuilder,
    tracks = 'tracks', 
    ecals = 'ecal_clusters', 
    hcals = 'hcal_clusters', 
    history = 'history_nodes',  
    output_blocks = 'reconstruction_blocks'
)


#reconstruct particles from blocks
from heppy.analyzers.PapasPFReconstructor import PapasPFReconstructor
pfreconstruct = cfg.Analyzer(
    PapasPFReconstructor,
    instance_label = 'papas_PFreconstruction', 
    detector = detector,
    input_blocks = 'reconstruction_blocks',
    history = 'history_nodes',     
    output_particles_dict = 'particles_dict', 
    output_particles_list = 'particles_list'
)



# Use a Filter to select leptons from the output of papas simulation.
# Currently, we're treating electrons and muons transparently.
# we could use two different instances for the Filter module
# to get separate collections of electrons and muons
# help(Filter) for more information
from heppy.analyzers.Filter import Filter
select_leptons = cfg.Analyzer(
    Filter,
    'sel_all_leptons',
    output = 'sim_leptons',
    input_objects = 'papas_sim_particles',
    filter_func = lambda ptc: abs(ptc.pdgid()) in [11, 13]
)

# Applying a simple resolution and efficiency model to electrons and muons.
# Indeed, papas simply copies generated electrons and muons
# from its input gen particle collection to its output reconstructed
# particle collection.
# Setting up the electron and muon models is left to the user,
# and the LeptonSmearer is just an example
# help(LeptonSmearer) for more information
from heppy.analyzers.examples.zh.LeptonSmearer import LeptonSmearer
smear_leptons = cfg.Analyzer(
    LeptonSmearer,
    'smear_leptons',
    output = 'smeared_leptons',
    input_objects = 'sim_leptons',
)


#merge smeared leptons with the reconstructed particles
from heppy.analyzers.Merger import Merger
merge_particles = cfg.Analyzer(
    Merger,
    instance_label = 'merge_particles', 
    inputA = 'papas_PFreconstruction_particles_list',
    inputB = 'smeared_leptons',
    output = 'rec_particles', 
)

papas_sequence = [
    gen_particles_stable,
    papas,
    pfblocks,
    pfreconstruct,
    select_leptons,
    smear_leptons, 
    merge_particles, 
]
