'''Example configuration file to produce various papas plots for an ee->ZH->mumubb analysis in heppy, with the FCC-ee
'''

import os
import copy
import heppy.framework.config as cfg

import logging

# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)

# global logging level for the heppy framework.
# in addition, all the analyzers declared below have their own logger,
# an each of them can be set to a different logging level.
logging.basicConfig(level=logging.WARNING)

# setting the random seed for reproducible results
import heppy.statistics.rrandom as random
# do not forget to comment out the following line if you want to produce and combine
# several samples of events 
random.seed(0xdeadbeef)

# loading the FCC event data model library to decode
# the format of the events in the input file
# help(Events) for more information 
from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events

# setting the event printout
# help(Event) for more information
from heppy.framework.event import Event
# comment the following line to see all the collections stored in the event 
Event.print_patterns=['zeds*', 'higgs*', 'rec_particles', 'gen_particles_stable', 'recoil*']

# definition of the collider
# help(Collider) for more information
from heppy.configuration import Collider
Collider.BEAMS = 'ee'
Collider.SQRTS = 240.

# definition of an input sample (also called a component)
# help(comp) for more information
#comp = cfg.Component(
    #'ee_ZH_Zmumu_Hbb',
    #files = [
        ## here we have a single input root file.
        ## the absolute path must be used to be able to run on the batch.
        #os.path.abspath('ee_ZH_Zmumu_Hbb.root')
    #]
#)
comp = cfg.Component(
    'ee_ZH_Zmumu_Hbb',
    files = [
        # here we have a single input root file.
        # the absolute path must be used to be able to run on the batch.
        os.path.abspath('ee_ZH_Zmumu_Hbb.root')
    ]
)

# selecting the list of components to be processed. Here only one. 
selectedComponents = [comp]

# read FCC EDM events from the input root file(s)
# do help(Reader) for more information
from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    gen_particles = 'GenParticle',
    gen_vertices = 'GenVertex'
)

# importing the papas simulation and reconstruction sequence,
# as well as the detector used in papas
# check papas_cfg.py for more information
from heppy.test.papas_cfg import papas_sequence, detector


from heppy.analyzers.PapasHistoryPrinter import PapasHistoryPrinter
papas_print_history = cfg.Analyzer(
    PapasHistoryPrinter,
    format = "subgroups",
    num_subgroups = 3 # biggest 3 subgroups will be printed
)


from heppy.analyzers.PapasHistoryPrinter import PapasHistoryPrinter
papas_print_history_event = cfg.Analyzer(
    PapasHistoryPrinter,
    format = "event"
)

#from heppy.analyzers.PapasDisplay import PapasDisplay
#papas_event_plot = cfg.Analyzer(
    #PapasDisplay,
    #projections = ['xy', 'yz'],
    #screennames = ["simulated", "reconstructed"],
    #particles_type_and_subtypes = ['ps', 'pr'],
    #clusters_type_and_subtypes = [['es', 'hs'],['em', 'hm']], 
    #detector = detector,
    #plottype = "event",
    ##save = True, todo
    #display = True
#)



from heppy.analyzers.PapasDagPlotter import PapasDAGPlotter
papas_dag_plot= cfg.Analyzer(
    PapasDAGPlotter,
    plottype = "event",
    show_file = False
)

from heppy.analyzers.PapasDagPlotter import PapasDAGPlotter
papas_dag_subgroups= cfg.Analyzer(
    PapasDAGPlotter,
    plottype = "subgroups",
    show_file = False,
    num_subgroups = 4
)

# Use a Selector to select leptons from the output of papas simulation.
# Currently, we're treating electrons and muons transparently.
# we could use two different instances for the Selector module
# to get separate collections of electrons and muons
# help(Selector) for more information
from heppy.analyzers.Selector import Selector
leptons_true = cfg.Analyzer(
    Selector,
    'sel_leptons',
    output = 'leptons_true',
    input_objects = 'rec_particles',
    filter_func = lambda ptc: ptc.e()>10. and abs(ptc.pdgid()) in [11, 13]
)

# Compute lepton isolation w/r other particles in the event.
# help(IsolationAnalyzer) for more information
from heppy.analyzers.IsolationAnalyzer import IsolationAnalyzer
from heppy.particles.isolation import EtaPhiCircle
iso_leptons = cfg.Analyzer(
    IsolationAnalyzer,
    candidates = 'leptons_true',
    particles = 'rec_particles',
    iso_area = EtaPhiCircle(0.4)
)

# Select isolated leptons with a Selector
# one can pass a function like this one to the filter:
def relative_isolation(lepton):
    sumpt = lepton.iso_211.sumpt + lepton.iso_22.sumpt + lepton.iso_130.sumpt
    sumpt /= lepton.pt()
    return sumpt
# ... or use a lambda statement as done below. 
sel_iso_leptons = cfg.Analyzer(
    Selector,
    'sel_iso_leptons',
    output = 'sel_iso_leptons',
    input_objects = 'leptons_true',
    # filter_func = relative_isolation
    filter_func = lambda lep : lep.iso.sumpt/lep.pt()<0.3 # fairly loose
)

# Building Zeds
# help(ResonanceBuilder) for more information
from heppy.analyzers.ResonanceBuilder import ResonanceBuilder
zeds = cfg.Analyzer(
    ResonanceBuilder,
    output = 'zeds',
    leg_collection = 'sel_iso_leptons',
    pdgid = 23
)

# Computing the recoil p4 (here, p_initial - p_zed)
# help(RecoilBuilder) for more information
sqrts = Collider.SQRTS 

from heppy.analyzers.RecoilBuilder import RecoilBuilder
recoil = cfg.Analyzer(
    RecoilBuilder,
    instance_label = 'recoil',
    output = 'recoil',
    sqrts = sqrts,
    to_remove = 'zeds_legs'
) 

missing_energy = cfg.Analyzer(
    RecoilBuilder,
    instance_label = 'missing_energy',
    output = 'missing_energy',
    sqrts = sqrts,
    to_remove = 'rec_particles'
) 

# Creating a list of particles excluding the decay products of the best zed.
# help(Masker) for more information
from heppy.analyzers.Masker import Masker
particles_not_zed = cfg.Analyzer(
    Masker,
    output = 'particles_not_zed',
    input = 'rec_particles',
    mask = 'zeds_legs',
)

# Make jets from the particles not used to build the best zed.
# Here the event is forced into 2 jets to target ZH, H->b bbar)
# help(JetClusterizer) for more information
from heppy.analyzers.fcc.JetClusterizer import JetClusterizer
jets = cfg.Analyzer(
    JetClusterizer,
    output = 'jets',
    particles = 'particles_not_zed',
    fastjet_args = dict( njets = 2)  
)

#TODO add b tagging, gen jets, gen jet matching

# Build Higgs candidates from pairs of jets.
higgses = cfg.Analyzer(
    ResonanceBuilder,
    output = 'higgses',
    leg_collection = 'jets',
    pdgid = 25
)


# Just a basic analysis-specific event Selection module.
# this module implements a cut-flow counter
# After running the example as
#    heppy_loop.py Trash/ analysis_ee_ZH_cfg.py -f -N 100 
# this counter can be found in:
#    Trash/example/heppy.analyzers.examples.zh.selection.Selection_cuts/cut_flow.txt
# Counter cut_flow :
#         All events                                     100      1.00    1.0000
#         At least 2 leptons                              87      0.87    0.8700
#         Both leptons e>30                               79      0.91    0.7900
# For more information, check the code of the Selection class
# in heppy/analyzers/examples/zh/selection.py
from heppy.analyzers.examples.zh.selection import Selection
selection = cfg.Analyzer(
    Selection,
    instance_label='cuts'
)

# Analysis-specific ntuple producer
# please have a look at the code of the ZHTreeProducer class,
# in heppy/analyzers/examples/zh/ZHTreeProducer.py
from heppy.analyzers.examples.zh.ZHTreeProducer import ZHTreeProducer
tree = cfg.Analyzer(
    ZHTreeProducer,
    zeds = 'zeds',
    jets = 'jets',
    higgses = 'higgses',
    recoil  = 'recoil',
    misenergy = 'missing_energy'
)

# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence(
    source,
    papas_sequence,
    #papas_print_history, 
    #papas_print_history_event, 
    #papas_event_plot, 
    #papas_event_subplot,
    papas_dag_plot, 
    #papas_dag_subgroups, 
    leptons_true,
    iso_leptons,
    sel_iso_leptons,
    zeds,
    recoil,
    missing_energy,
    particles_not_zed,
    jets,
    higgses,
    selection, 
    tree
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
    import heppy.statistics.rrandom as random
    from heppy.papas.data.identifier import Identifier
    random.seed(0xdeadbeef)

    def process(iev=None):
        if iev is None:
            iev = loop.iEvent
        loop.process(iev)
        display = False #only display first event in a loop

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
    display = False
    if len(sys.argv)==2:
        display = True
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
                   nPrint=1,
                   timeReport=True)
    
    for ana in loop.analyzers: 
        if hasattr(ana, 'display') and ana.display == True:
            display = True # will display first event in a loop
    
    if iev is not None:
        process(iev)
        pass
    else:
        loop.loop()
        loop.write()
