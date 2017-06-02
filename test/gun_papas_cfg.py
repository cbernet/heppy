'''Example configuration file a particle gun in heppy, with the FCC-ee

While studying this file, open it in ipython as well as in your editor to 
get more information: 

ipython
from gun_papas_cfg import * 
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
# if collection is listed then print loop.event.papasevent will include the collections
Event.print_patterns=['zeds*', 'higgs*', 'rec_particles', 'gen_particles_stable', 'recoil*', 'collections']

# definition of the collider
# help(Collider) for more information
from heppy.configuration import Collider
Collider.BEAMS = 'ee'
Collider.SQRTS = 240.

pdgid = [211, 130]

# dummy input component (we use a particle gun)
comp = cfg.Component(
    'gun_{}'.format(pdgid),
    files = [None]
)


from heppy.analyzers.PapasDagPlotter import PapasDAGPlotter
papas_dag_plot= cfg.Analyzer(
    PapasDAGPlotter,
    plottype = "dag_event",
    show_file = False
)

# selecting the list of components to be processed. Here only one. 
selectedComponents = [comp]

# particle gun analyzer
import math
from heppy.analyzers.Gun import Gun
source = cfg.Analyzer(
    Gun,
    pdgid = pdgid,
    thetamin = -0.1,
    thetamax = 0.1,
    phimin = math.pi/2.,
    phimax = math.pi/2.,
    ptmin = 5,
    ptmax = 10,
    flat_pt = False,
    papas = True
)

# importing the papas simulation and reconstruction sequence,
# as well as the detector used in papas
# check papas_cfg.py for more information
from heppy.test.papas_cfg import papas, papas_sequence, detector

from heppy.test.papas_cfg import papasdisplay as display 

from heppy.analyzers.P4SumBuilder import P4SumBuilder
sum_particles = cfg.Analyzer(
    P4SumBuilder, 
    output='sum_all_ptcs',
    #    particles='gen_particles_stable'
    particles='rec_particles'
)

sum_gen = cfg.Analyzer(
    P4SumBuilder, 
    output='sum_all_gen',
    particles='gen_particles_stable'
)


from heppy.analyzers.GlobalEventTreeProducer import GlobalEventTreeProducer
zed_tree = cfg.Analyzer(
    GlobalEventTreeProducer, 
    sum_all='sum_all_ptcs', 
    sum_all_gen='sum_all_gen'
)

# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence(
    source, 
    papas_sequence,
    display
)

# Specifics for particle gun events
from ROOT import gSystem
from heppy.framework.eventsgen import Events

config = cfg.Config(
    components = selectedComponents,
    sequence = sequence,
    services = [],
    events_class = Events
)
