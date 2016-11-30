import heppy.framework.config as cfg
from heppy.configuration import Collider
import logging


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
    particles_type_and_subtypes = ['ps'],
    clusters_type_and_subtypes = [['es', 'hs']], 
    #display_filter_func = lambda ptc: ptc.e()>1.,
    do_display = False
)

papasdisplaycompare = cfg.Analyzer(
    PapasDisplay,
    projections = ['xy', 'yz'],
    screennames = ["simulated", "reconstructed"],
    particles_type_and_subtypes = ['ps', 'pr'],
    clusters_type_and_subtypes = [['es', 'hs'],['em', 'hm']],
    detector = detector,
    #save = True,
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
    # instance_label = 'papas_PFreconstruction', 
    detector = detector,
    output = 'rec_particles',
    log_level=logging.WARNING
)

papas_sequence = [
    gen_particles_stable,
    papas,
    pfblocks,
    pfreconstruct,
]
