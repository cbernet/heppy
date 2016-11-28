import heppy.framework.config as cfg
from heppy.configuration import Collider

# Use a Selector to select stable gen particles for simulation
# from the output of "source" 
# help(Selector) for more information
from heppy.analyzers.Selector import Selector
gen_particles_stable = cfg.Analyzer(
    Selector,
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
    verbose = True
)

from heppy.analyzers.PapasDisplay import PapasDisplay
papasdisplay = cfg.Analyzer(
    PapasDisplay,
    instance_label = 'papas',
    detector = detector,
    projections = ['xy', 'yz'],
    screennames = ["simulated"],#["reconstructed"],#
    particles_type_and_subtype = 'ps',
    clusters_type_and_subtypes = ['es','hs'],
    #display_filter_func = lambda ptc: ptc.e()>1.,
    #todo save option
    do_display = False
)

# group the clusters, tracks from simulation into connected blocks ready for reconstruction
from heppy.analyzers.PapasPFBlockBuilder import PapasPFBlockBuilder
pfblocks = cfg.Analyzer(
    PapasPFBlockBuilder,
    track_type_and_subtype = 'ts', 
    ecal_type_and_subtype = 'em', 
    hcal_type_and_subtype = 'hm'
)

#reconstruct particles from blocks
from heppy.analyzers.PapasPFReconstructor import PapasPFReconstructor
pfreconstruct = cfg.Analyzer(
    PapasPFReconstructor,
    track_type_and_subtype = 'ts', 
    ecal_type_and_subtype = 'em', 
    hcal_type_and_subtype = 'hm',
    block_type_and_subtype = 'br',
    instance_label = 'papas_PFreconstruction', 
    detector = detector,
    output_particles_list = 'particles_list'
)

# Use a Selector to select leptons from the output of papas simulation.
# Currently, we're treating electrons and muons transparently.
# we could use two different instances for the Selector module
# to get separate collections of electrons and muons
# help(Selector) for more information
from heppy.analyzers.Selector import Selector
sim_electrons = cfg.Analyzer(
    Selector,
    'sim_electrons',
    output = 'sim_electrons',
    input_objects = 'papas_sim_particles',
    filter_func = lambda ptc: abs(ptc.pdgid()) in [11]
)

sim_muons = cfg.Analyzer(
    Selector,
    'sim_muons',
    output = 'sim_muons',
    input_objects = 'papas_sim_particles',
    filter_func = lambda ptc: abs(ptc.pdgid()) in [13]
)


# Applying a simple resolution and efficiency model to electrons and muons.
# Indeed, papas simply copies generated electrons and muons
# from its input gen particle collection to its output reconstructed
# particle collection.
# Setting up the electron and muon models is left to the user,
# and the LeptonSmearer is just an example
# help(LeptonSmearer) for more information
from heppy.analyzers.GaussianSmearer import GaussianSmearer     
def accept_electron(ele):
    return abs(ele.eta()) < 2.5 and ele.e() > 5.
electrons = cfg.Analyzer(
    GaussianSmearer,
    'electrons',
    output = 'electrons',
    input_objects = 'sim_electrons',
    accept=accept_electron, 
    mu_sigma=(1, 0.1)
    )

def accept_muon(mu):
    return abs(mu.eta()) < 2.5 and mu.pt() > 5.
muons = cfg.Analyzer(
    GaussianSmearer,
    'muons',
    output = 'muons',
    input_objects = 'sim_muons',
    accept=accept_muon, 
    mu_sigma=(1, 0.02)
    )

#merge smeared leptons with the reconstructed particles
from heppy.analyzers.Merger import Merger
from heppy.particles.p4 import P4
merge_particles = cfg.Analyzer(
    Merger,
    instance_label = 'merge_particles',
    inputs=['papas_PFreconstruction_particles_list', 'electrons', 'muons'], 
    output = 'rec_particles',
    sort_key = P4.sort_key
)

papas_sequence = [
    gen_particles_stable,
    papas,
    pfblocks,
    pfreconstruct,
    sim_electrons,
    sim_muons, 
    electrons,
    muons, 
    merge_particles, 
]
