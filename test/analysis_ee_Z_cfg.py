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
Event.print_patterns=['sum*']

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
Collider.SQRTS = 91.
do_clic = False

# input definition
import glob
ee_Z_ddbar = cfg.Component(
    'ee_Z_ddbar',
    files = ['data/ee_Z_ddbar.root'] 
    )
ee_Z_ddbar.splitFactor = len(ee_Z_ddbar.files)

ee_Z_bbbar = cfg.Component(
    'ee_Z_bbbar',
    files = ['data/ee_Z_bbbar.root']
)


selectedComponents = [ee_Z_ddbar]

# read FCC EDM events from the input root file(s)
# do help(Reader) for more information
from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    gen_particles = 'GenParticle',
    gen_vertices = 'GenVertex'
)

from heppy.analyzers.SingleJetBuilder import SingleJetBuilder
sum_particles = cfg.Analyzer(
    SingleJetBuilder, 
    output='sum_all_ptcs',
    #    particles='gen_particles_stable'
    particles='rec_particles'
)

sum_gen = cfg.Analyzer(
    SingleJetBuilder, 
    output='sum_all_gen',
    particles='gen_particles_stable'
)


from heppy.analyzers.GlobalEventTreeProducer import GlobalEventTreeProducer
zed_tree = cfg.Analyzer(
    GlobalEventTreeProducer, 
    sum_all='sum_all_ptcs', 
    sum_all_gen='sum_all_gen'
)


from heppy.test.papas_cfg import gen_particles_stable, papas_sequence, detector, papas, papasdisplay, papasdisplaycompare, pfreconstruct
from heppy.test.papas_cfg import papasdisplaycompare as display

if do_clic:
    from heppy.papas.detectors.CLIC import clic
    papas.detector = clic    
    display.detector = clic
    pfreconstruct.detector = clic

from heppy.test.pdebug_cfg import pdebug

# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence(
    source,
    pdebug,
    # gen_particles_stable, 
    papas_sequence,
    sum_particles,
    sum_gen, 
    zed_tree,
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

