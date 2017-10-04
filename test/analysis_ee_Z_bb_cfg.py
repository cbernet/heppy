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

from heppy.configuration import from_fccsw

# input definition
ee_Z_bbbar = cfg.Component(
    'ee_Z_bbbar',
    files = [
        'data/ee_Z_bbbar.root'
    ]
)

selectedComponents = [ee_Z_bbbar]

if from_fccsw :
    from heppy.test.fccsw_cf import source, papas_process
else:
    # read FCC EDM events from the input root file(s)
    # do help(Reader) for more information
    from heppy.analyzers.fcc.Reader import Reader
    source = cfg.Analyzer(
        Reader,
        gen_particles = 'GenParticle',
        gen_vertices = 'GenVertex'
    )
    from heppy.test.papas_cfg import gen_particles_stable, detector, papas, papasdisplay
    from heppy.test.papas_cfg import  papas_sequence as papas_process
 

from heppy.test.papas_cfg import papasdisplaycompare as display 

# Make jets 
from heppy.analyzers.fcc.JetClusterizer import JetClusterizer
jets = cfg.Analyzer(
    JetClusterizer,
    output = 'jets',
    particles = 'rec_particles',
    fastjet_args = dict( njets = 2 ),
    njets_required=False
)

# b tagging, parametrized
from heppy.test.btag_parametrized_cfg import btag_parametrized, btag
from heppy.analyzers.roc import cms_roc
btag.roc = cms_roc

## b tagging, IP smearing
#from heppy.test.btag_ip_smearing_2_cfg import btag_ip_smearing

do_clic = False
if do_clic:
    from heppy.papas.detectors.CLIC import clic
    papas.detector = clic    
    display.detector = clic
    #TODO replace by clic ROC!


from heppy.analyzers.JetTreeProducer import JetTreeProducer
jet_tree = cfg.Analyzer(
    JetTreeProducer,
    tree_name = 'events',
    tree_title = 'jets',
    jets = 'jets',
    taggers = ['b', 'bmatch', 'bfrac'], 
    njets = 2, 
    store_match =False
)

from heppy.test.pdebug_cfg import pdebug

# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence(
    source,
    #pdebug,
    papas_process,
    jets, 
    btag_parametrized,
    jet_tree, 
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

