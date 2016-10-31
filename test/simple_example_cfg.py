
import os
import heppy.framework.config as cfg
import logging
logging.basicConfig(level=logging.INFO)

# input component 
# several input components can be declared,
# and added to the list of selected components

inputSample = cfg.Component(
    'test_component',
    # create the test file by running
    # python create_tree.py
    files = [os.path.abspath('test_tree.root')],
    )

selectedComponents  = [inputSample]

# use a simple event reader based on the ROOT TChain class
from heppy.framework.chain import Chain as Events

# add a random variable to the event 
from heppy.analyzers.examples.simple.RandomAnalyzer import RandomAnalyzer
random = cfg.Analyzer(
    RandomAnalyzer
    )

# just print a variable in the input test tree
from heppy.analyzers.examples.simple.Printer import Printer
printer = cfg.Analyzer(
    Printer,
    log_level=logging.INFO
    )

# illustrates how to use an exception to stop processing at event 10
# for debugging purposes.
from heppy.analyzers.examples.simple.Stopper import Stopper
stopper = cfg.Analyzer(
    Stopper,
    iEv = 10
    )

# creating a simple output tree
from heppy.analyzers.examples.simple.SimpleTreeProducer import SimpleTreeProducer
tree = cfg.Analyzer(
    SimpleTreeProducer,
    tree_name = 'tree',
    tree_title = 'A test tree'
    )


# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence([
        random,
        # printer,
        # stopper,
        tree,
] )

from heppy.framework.services.tfile import TFileService
output_rootfile = cfg.Service(
    TFileService,
    'myhists',
    fname='histograms.root',
    option='recreate'
)

services = [output_rootfile]

# finalization of the configuration object. 
config = cfg.Config( components = selectedComponents,
                     sequence = sequence,
                     services = services, 
                     events_class = Events )

# print config 
