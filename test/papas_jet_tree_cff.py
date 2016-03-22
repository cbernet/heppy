import heppy.framework.config as cfg

jet_tree_sequence = []

from heppy.analyzers.fcc.JetClusterizer import JetClusterizer
gen_jets = cfg.Analyzer(
    JetClusterizer,
    output = 'gen_jets',
    particles = 'gen_particles_stable',
    fastjet_args = dict(ptmin = 0.5),
    )
    
jets = cfg.Analyzer(
    JetClusterizer,
    output = 'jets', 
    particles = 'papas_rec_particles',
    fastjet_args = dict(ptmin = 0.5),
    )

from heppy.analyzers.Matcher import Matcher
jet_match = cfg.Analyzer(
    Matcher,
    match_particles = 'gen_jets',
    particles = 'jets',
    delta_r = 0.3
    )

from heppy.analyzers.JetTreeProducer import JetTreeProducer
jet_tree = cfg.Analyzer(
    JetTreeProducer,
    tree_name = 'events',
    tree_title = 'jets',
    jets = 'jets'
    )

papas_jet_tree_sequence = [
    gen_jets, jets, jet_match, jet_tree
    ]
