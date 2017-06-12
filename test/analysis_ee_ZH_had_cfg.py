'''Example configuration file for an ee->ZH analysis in the 4 jet channel,
with the FCC-ee

While studying this file, open it in ipython as well as in your editor to 
get more information: 

ipython
from analysis_ee_ZH_had_cfg import * 

'''

import os
import copy
import heppy.framework.config as cfg

from heppy.framework.event import Event
Event.print_patterns=['*jet*', 'bquarks', '*higgs*',
                      '*zed*', '*lep*']

import logging
# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)
logging.basicConfig(level=logging.WARNING)

# setting the random seed for reproducible results
import heppy.statistics.rrandom as random
random.seed(0xdeadbeef)

# definition of the collider
from heppy.configuration import Collider
Collider.BEAMS = 'ee'
Collider.SQRTS = 240.

# input definition
comp = cfg.Component(
    'ee_ZH_Z_Hbb',
    files = [
        'ee_ZH_Z_Hbb.root'
    ]
)
selectedComponents = [comp]

# read FCC EDM events from the input root file(s)
# do help(Reader) for more information
from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    gen_particles = 'GenParticle',
    gen_vertices = 'GenVertex'
)

# the papas simulation and reconstruction sequence
from heppy.test.papas_cfg import papas_sequence, detector
from heppy.test.papas_cfg import papasdisplay as display

# Use a Selector to select leptons from the output of papas simulation.
# Currently, we're treating electrons and muons transparently.
# we could use two different instances for the Selector module
# to get separate collections of electrons and muons
# help(Selector) for more information
from heppy.analyzers.Selector import Selector
def is_lepton(ptc):
    return ptc.e()> 5. and abs(ptc.pdgid()) in [11, 13]

leptons = cfg.Analyzer(
    Selector,
    'sel_leptons',
    output = 'leptons',
    input_objects = 'rec_particles',
    filter_func = is_lepton 
)

# Compute lepton isolation w/r other particles in the event.
# help(IsolationAnalyzer) 
# help(isolation) 
# for more information
from heppy.analyzers.IsolationAnalyzer import IsolationAnalyzer
from heppy.particles.isolation import EtaPhiCircle
iso_leptons = cfg.Analyzer(
    IsolationAnalyzer,
    candidates = 'leptons',
    particles = 'rec_particles',
    iso_area = EtaPhiCircle(0.4)
)

# Select isolated leptons with a Selector
def is_isolated(lep):
    '''returns true if the particles around the lepton
    in the EtaPhiCircle defined above carry less than 30%
    of the lepton energy.'''
    return lep.iso.sume/lep.e()<0.3  # fairly loose

sel_iso_leptons = cfg.Analyzer(
    Selector,
    'sel_iso_leptons',
    output = 'sel_iso_leptons',
    input_objects = 'leptons',
    filter_func = is_isolated
)


##Rejecting events that contain a loosely isolated lepton
##
##Instead of using an event filter at this stage, we store in the tree
##the lepton with lowest energy (with the name lepton1)
##
##from heppy.analyzers.EventFilter import EventFilter
##lepton_veto = cfg.Analyzer(
##    EventFilter,
##    'lepton_veto',
##    input_objects='sel_iso_leptons',
##    min_number=1,
##    veto=True
##)

# compute the missing 4-momentum
from heppy.analyzers.RecoilBuilder import RecoilBuilder
missing_energy = cfg.Analyzer(
    RecoilBuilder,
    instance_label = 'missing_energy',
    output = 'missing_energy',
    sqrts = Collider.SQRTS,
    to_remove = 'rec_particles'
) 


# make 4 exclusive jets 
from heppy.analyzers.fcc.JetClusterizer import JetClusterizer
jets = cfg.Analyzer(
    JetClusterizer,
    output = 'jets',
    particles = 'rec_particles',
    fastjet_args = dict( njets = 4)  
)

# make 4 gen jets with stable gen particles
genjets = cfg.Analyzer(
    JetClusterizer,
    output = 'genjets',
    particles = 'gen_particles_stable',
    fastjet_args = dict( njets = 4)  
)

# select b quarks for jet to parton matching
def is_bquark(ptc):
    '''returns True if the particle is an outgoing b quark,
    see
    http://home.thep.lu.se/~torbjorn/pythia81html/ParticleProperties.html
    '''
    return abs(ptc.pdgid()) == 5 and ptc.status() == 23
    
bquarks = cfg.Analyzer(
    Selector,
    'bquarks',
    output = 'bquarks',
    input_objects = 'gen_particles',
    filter_func =is_bquark
)

# match genjets to b quarks 
from heppy.analyzers.Matcher import Matcher
genjet_to_b_match = cfg.Analyzer(
    Matcher,
    match_particles = 'bquarks',
    particles = 'genjets',
    delta_r = 0.4
    )

# match jets to genjets (so jets are matched to b quarks through gen jets)
jet_to_genjet_match = cfg.Analyzer(
    Matcher,
    match_particles='genjets',
    particles='rescaled_jets',
    delta_r=0.5
)

# rescale the jet energy taking according to initial p4
from heppy.analyzers.examples.zh_had.JetEnergyComputer import JetEnergyComputer
compute_jet_energy = cfg.Analyzer(
    JetEnergyComputer,
    output_jets='rescaled_jets',
    input_jets='jets',
    sqrts=Collider.SQRTS
    )

# parametrized b tagging with CMS performance.
# the performance of other detectors can be supplied
# in the roc module
# cms_roc is a numpy array, so one can easily scale
# the cms performance, help(numpy.array) for more info.

btag_type = 'smeared'
btag = None
if btag_type == 'parametrized':
    from heppy.analyzers.ParametrizedBTagger import ParametrizedBTagger
    from heppy.analyzers.roc import cms_roc
    cms_roc.set_working_point(0.7)
    btag = cfg.Analyzer(
        ParametrizedBTagger,
        input_jets='rescaled_jets',
        roc=cms_roc
    )
elif btag_type == 'smeared':
    def track_selection_function(track):
        return track.q() != 0 and \
        abs(track.path.smeared_impact_parameter) < 2.5e-3 and \
        track.path.ip_resolution < 7.5e-4 and \
        track.e() > 0.4
    
    import math
    def aleph_resolution(ptc):
        momentum = ptc.p3().Mag()
        return math.sqrt(25.**2 + 95.**2/ (momentum**2) )*1e-6
    
    from heppy.analyzers.ImpactParameterJetTag import ImpactParameterJetTag
    btag = cfg.Analyzer(
        ImpactParameterJetTag,
        jets = 'jets',
        method = 'simple',
        track_selection = track_selection_function,
        resolution = aleph_resolution,
        #mva attributes, not mandatory
        mva_filename = '../02_b_tagging/18_without_beampipe_simple_ILD/ntuple/qq_ILD_spIP/analyzers.ZqqIPJetsTreeProducer.ZqqIPJetsTreeProducer_1/tree.root',
        mva_treename = 'events',
        mva_background_selection = 'quark_type <= 4',
        mva_signal_selection = 'quark_type == 5',
    )    

# reconstruction of the H and Z resonances.
# for now, use for the Higgs the two b jets with the mass closest to mH
# the other 2 jets are used for the Z.
# implement a chi2? 
from heppy.analyzers.examples.zh_had.ZHReconstruction import ZHReconstruction
zhreco = cfg.Analyzer(
    ZHReconstruction,
    output_higgs='higgs',
    output_zed='zed', 
    input_jets='rescaled_jets'
)

# simple cut flow printout
from heppy.analyzers.examples.zh_had.Selection import Selection
selection = cfg.Analyzer(
    Selection,
    input_jets='rescaled_jets', 
    log_level=logging.INFO
)

# Analysis-specific ntuple producer
# please have a look at the ZHTreeProducer class
from heppy.analyzers.examples.zh_had.TreeProducer import TreeProducer
tree = cfg.Analyzer(
    TreeProducer,
    misenergy = 'missing_energy', 
    jets='rescaled_jets',
    higgs='higgs',
    zed='zed',
    leptons='sel_iso_leptons'
)

# definition of the sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence(
    source,
    papas_sequence, 
    leptons,
    iso_leptons,
    sel_iso_leptons,
#    lepton_veto, 
    jets,
    compute_jet_energy, 
    bquarks,
    genjets, 
    genjet_to_b_match,
    jet_to_genjet_match, 
    btag,
    missing_energy, 
    selection, 
    zhreco, 
    tree,
    display
)

# Specifics to read FCC events 
from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events

config = cfg.Config(
    components = selectedComponents,
    sequence = sequence,
    services = [],
    events_class = Events
)

