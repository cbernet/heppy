import heppy.framework.config as cfg

def jet_tree_sequence(gen_ptcs, rec_ptcs):

    from heppy.analyzers.fcc.JetClusterizer import JetClusterizer
    gen_jets = cfg.Analyzer(
        JetClusterizer,
        output = 'gen_jets',
        particles = gen_ptcs,
        fastjet_args = dict(ptmin = 0.5),
        )

    jets = cfg.Analyzer(
        JetClusterizer,
        output = 'jets', 
        particles = rec_ptcs,
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

    return [gen_jets, jets, jet_match, jet_tree]
