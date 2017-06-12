import heppy.framework.config as cfg

def jet_tree_sequence(gen_ptcs, rec_ptcs, njets=None, ptmin=None):
    '''returns this sequence:
    
        return ( {'gen_jets': gen_jets,
              'jets': jets,
              'jet_match': jet_match,
              'jet_tree': jet_tree},
             sequence )
             
    @param gen_ptcs: gen particles to be used for gen jets
    @param rec_ptcs: rec particles to be used for rec jets
    @param njets: number of jets in exclusive mode
    @param ptmin: minimum jet pt in inclusive mode
    '''
    fastjet_args = None
    if njets:
        fastjet_args = dict(njets=njets)
    elif ptmin is not None:
        fastjet_args = dict(ptmin=ptmin)
    else:
        raise ValueError('provide either njets or ptmin')
    
    from heppy.analyzers.fcc.JetClusterizer import JetClusterizer
    gen_jets = cfg.Analyzer(
        JetClusterizer,
        output = 'gen_jets',
        particles = gen_ptcs,
        fastjet_args = fastjet_args,
        )

    jets = cfg.Analyzer(
        JetClusterizer,
        output = 'jets', 
        particles = rec_ptcs,
        fastjet_args = fastjet_args,
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

    sequence = [gen_jets, jets, jet_match, jet_tree]
    return ( {'gen_jets': gen_jets,
              'jets': jets,
              'jet_match': jet_match,
              'jet_tree': jet_tree},
             sequence )
