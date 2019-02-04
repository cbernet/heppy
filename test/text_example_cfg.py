
import os
import heppy.framework.config as cfg
import logging
logging.basicConfig(level=logging.INFO)

# input component 
# several input components can be declared,
# and added to the list of selected components

from heppy.framework.test_eventstext import create_data

input_fname = create_data()

inputSample = cfg.Component(
    'test_component',
    # create the test file by running
    # python create_tree.py
    files = [input_fname],
    )

selectedComponents  = [inputSample]

# use a simple event reader based on the ROOT TChain class
from heppy.framework.eventstext import Events

# add a random variable to the event 
from heppy.analyzers.examples.simple.TextAnalyzer import TextAnalyzer   
text = cfg.Analyzer(
    TextAnalyzer
    )

# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence([
        text,
] )


# finalization of the configuration object. 
config = cfg.Config( components = selectedComponents,
                     sequence = sequence,
                     services = [], 
                     events_class = Events )



