'''Example configuration file for an ee->ZH->mumubb analysis in heppy, with the FCC-ee

While studying this file, open it in ipython as well as in your editor to 
get more information: 

ipython
from analysis_ee_ZH_cfg import * 
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
logging.basicConfig(level=logging.INFO)

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
# if collection is listed then print loop.event.papasevent will include the collections
# Event.print_patterns=['*']

# definition of the collider
# help(Collider) for more information
from heppy.configuration import Collider
Collider.BEAMS = 'ee'
Collider.SQRTS = 240.

# definition of an input sample (also called a component)
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
    input_objects = 'gen_particles',
    filter_func = lambda ptc: ptc.e()>10. and abs(ptc.pdgid()) in [11, 13] and ptc.status() == 1
)

# Building Zeds
# help(ResonanceBuilder) for more information
from heppy.analyzers.ResonanceBuilder import ResonanceBuilder
zeds = cfg.Analyzer(
    ResonanceBuilder,
    output = 'zeds',
    leg_collection = 'leptons_true',
    pdgid = 23
)

# select resonant candidates
select_zeds = cfg.Analyzer(
    Selector,
    output = 'sel_zeds',
    input_objects = 'zeds',
    filter_func = lambda ptc: abs(ptc.m() - 91) < 5.
)

# match all resonances to the resonant ones.
from heppy.analyzers.ResonanceMatcher import ResonanceMatcher
match = cfg.Analyzer(
    ResonanceMatcher,
    resonances='zeds',
    match_resonances='sel_zeds', 
    nmatch=2
)

# select unmatched resonances
unmatched_resonances = cfg.Analyzer(
    Selector,
    output = 'unmatched',
    input_objects = 'zeds',
    filter_func = lambda ptc: len(ptc.matches) == 0
)

# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence(
    source,
    leptons_true,
    zeds,
    select_zeds,
    match,
    unmatched_resonances
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
