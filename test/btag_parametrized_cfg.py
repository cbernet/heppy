import heppy.framework.config as cfg
from heppy.configuration import Collider

# select b quarks for jet to parton matching
def is_bquark(ptc):
    '''returns True if the particle is an outgoing b quark,
    see
    http://home.thep.lu.se/~torbjorn/pythia81html/ParticleProperties.html
    '''
    return abs(ptc.pdgid()) == 5 and ptc.status() == 23
    
from heppy.analyzers.Selector import Selector
bquarks = cfg.Analyzer(
    Selector,
    'bquarks',
    output = 'bquarks',
    input_objects = 'gen_particles',
    filter_func =is_bquark
)

# match jets to genjets (so jets are matched to b quarks through gen jets)
from heppy.analyzers.Matcher import Matcher
jet_to_bquark_match = cfg.Analyzer(
    Matcher,
    match_particles='bquarks',
    particles='jets',
    delta_r=0.5
)

from heppy.analyzers.ParametrizedBTagger import ParametrizedBTagger
from heppy.analyzers.roc import cms_roc
cms_roc.set_working_point(0.7)
btag = cfg.Analyzer(
    ParametrizedBTagger,
    input_jets='jets',
    roc=cms_roc
)

btag_parametrized = [
    bquarks,
    # jet_to_bquark_match,
    btag
]
