import os
import heppy.framework.config as cfg
from heppy.framework.chain import Chain as Events
from heppy.analyzers.Printer import Printer
from heppy.analyzers.SimpleTreeProducer import SimpleTreeProducer

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

printer = cfg.Analyzer(
    Printer
    )

tree = cfg.Analyzer(
    SimpleTreeProducer,
    tree_name = 'tree',
    tree_title = 'A test tree'
    )

# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence( [
    printer,
    tree
    ] )

# finalization of the configuration object. 
config = cfg.Config( components = selectedComponents,
                     sequence = sequence, 
                     events_class = Events )

print config 
