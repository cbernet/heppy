'''Example configuration file for an ee->ZH->mumubb analysis in heppy, with the FCC-ee

While studying this file, open it in ipython as well as in your editor to 
get more information: 

ipython
from analysis_ee_ZH_cfg import * 

'''

import os
import copy
import heppy.framework.config as cfg

from heppy.framework.event import Event
Event.print_patterns=['*jet*', 'bquarks', '*higgs*', '*zed*']

import logging
# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)
logging.basicConfig(level=logging.ERROR)

# setting the random seed for reproducible results
import heppy.statistics.rrandom as random
random.seed(0xdeadbeef)

# definition of the collider
from heppy.configuration import Collider
Collider.BEAMS = 'ee'
Collider.SQRTS = 240.

# input definition
comp = cfg.Component(
    'example',
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

from heppy.test.papas_cfg import papas_sequence, detector, papas

# Use a Filter to select leptons from the output of papas simulation.
# Currently, we're treating electrons and muons transparently.
# we could use two different instances for the Filter module
# to get separate collections of electrons and muons
# help(Filter) for more information
from heppy.analyzers.Filter import Filter
leptons = cfg.Analyzer(
    Filter,
    'sel_leptons',
    output = 'leptons',
    input_objects = 'rec_particles',
    filter_func = lambda ptc: ptc.e()> 5. and abs(ptc.pdgid()) in [11, 13]
)

# Compute lepton isolation w/r other particles in the event.
# help(LeptonAnalyzer) for more information
from heppy.analyzers.LeptonAnalyzer import LeptonAnalyzer
from heppy.particles.isolation import EtaPhiCircle
iso_leptons = cfg.Analyzer(
    LeptonAnalyzer,
    leptons = 'leptons',
    particles = 'rec_particles',
    iso_area = EtaPhiCircle(0.4)
)

# Select isolated leptons with a Filter
# one can pass a function like this one to the filter:
def relative_isolation(lepton):
    sumpt = lepton.iso_211.sumpt + lepton.iso_22.sumpt + lepton.iso_130.sumpt
    sumpt /= lepton.pt()
    return sumpt
# ... or use a lambda statement as done below. 
sel_iso_leptons = cfg.Analyzer(
    Filter,
    'sel_iso_leptons',
    output = 'sel_iso_leptons',
    input_objects = 'leptons',
    # filter_func = relative_isolation
    filter_func = lambda lep : lep.iso.sumpt/lep.pt()<0.3 # fairly loose
)


##Rejecting events that contain a loosely isolated lepton
##
##Instead of using an event filter at this stage, we store in the tree
##the lepton with lowest energy.
##
##from heppy.analyzers.EventFilter import EventFilter
##lepton_veto = cfg.Analyzer(
##    EventFilter,
##    'lepton_veto',
##    input_objects='sel_iso_leptons',
##    min_number=1,
##    veto=True
##)


from heppy.analyzers.RecoilBuilder import RecoilBuilder
missing_energy = cfg.Analyzer(
    RecoilBuilder,
    instance_label = 'missing_energy',
    output = 'missing_energy',
    sqrts = Collider.SQRTS,
    to_remove = 'rec_particles'
) 


# Make 4 jets 
from heppy.analyzers.fcc.JetClusterizer import JetClusterizer
jets = cfg.Analyzer(
    JetClusterizer,
    output = 'jets',
    particles = 'rec_particles',
    fastjet_args = dict( njets = 4)  
)

genjets = cfg.Analyzer(
    JetClusterizer,
    output = 'genjets',
    particles = 'gen_particles_stable',
    fastjet_args = dict( njets = 4)  
)

bquarks = cfg.Analyzer(
    Filter,
    'bquarks',
    output = 'bquarks',
    input_objects = 'gen_particles',
    filter_func = lambda ptc : abs(ptc.pdgid()) == 5 and ptc.status() == 23
)

from heppy.analyzers.Matcher import Matcher
genjet_to_b_match = cfg.Analyzer(
    Matcher,
    match_particles = 'bquarks',
    particles = 'genjets',
    delta_r = 0.4
    )

jet_to_genjet_match = cfg.Analyzer(
    Matcher,
    match_particles='genjets',
    particles='rescaled_jets',
    delta_r=0.5
)

from heppy.analyzers.examples.zh_had.JetEnergyComputer import JetEnergyComputer
compute_jet_energy = cfg.Analyzer(
    JetEnergyComputer,
    output_jets='rescaled_jets',
    input_jets='jets'
    )

from heppy.analyzers.ParametrizedBTagger import ParametrizedBTagger
from heppy.analyzers.roc import cms_roc
cms_roc.set_working_point(0.7)
btag = cfg.Analyzer(
    ParametrizedBTagger,
    input_jets='rescaled_jets',
    roc=cms_roc
)

from heppy.analyzers.examples.zh_had.Selection import Selection
selection = cfg.Analyzer(
    Selection,
)

# Analysis-specific ntuple producer
# please have a look at the ZHTreeProducer class
##from heppy.analyzers.examples.zh_had.TreeProducer import TreeProducer
##tree = cfg.Analyzer(
##    TreeProducer,
##    zed = 'zed',
##    higg = 'higg',
##    misenergy = 'missing_energy'
##)

# definition of a sequence of analyzers,
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
    selection
#    zeds,
#    higgses,
#    selection, 
#    tree
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

if __name__ == '__main__':
    import sys
    from heppy.framework.looper import Looper

    def process(iev=None):
        if iev is None:
            iev = loop.iEvent
        loop.process(iev)
        if display:
            display.draw()

    def next():
        loop.process(loop.iEvent+1)
        if display:
            display.draw()            

    iev = None
    usage = '''usage: python analysis_ee_ZH_cfg.py [ievent]
    
    Provide ievent as an integer, or loop on the first events.
    You can also use this configuration file in this way: 
    
    heppy_loop.py OutDir/ analysis_ee_ZH_cfg.py -f -N 100 
    '''
    if len(sys.argv)==2:
        papas.display = True
        try:
            iev = int(sys.argv[1])
        except ValueError:
            print usage
            sys.exit(1)
    elif len(sys.argv)>2: 
        print usage
        sys.exit(1)
            
        
    loop = Looper( 'looper', config,
                   nEvents=10,
                   nPrint=10,
                   timeReport=True)
    
    simulation = None
    for ana in loop.analyzers: 
        if hasattr(ana, 'display'):
            simulation = ana
    display = getattr(simulation, 'display', None)
    simulator = getattr(simulation, 'simulator', None)
    if simulator: 
        detector = simulator.detector
    if iev is not None:
        process(iev)
    else:
        loop.loop()
        loop.write()
