import os
import copy
import heppy.framework.config as cfg

import logging
# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)
logging.basicConfig(level=logging.WARNING)

comp = cfg.Component(
    'example',
    files = ['FCCDelphesOutput.root']
   )
selectedComponents = [comp]

from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,

    fatjets = 'fatjets',
    jetsOneSubJettiness = 'jetsOneSubJettiness', 
    jetsTwoSubJettiness = 'jetsTwoSubJettiness', 
    jetsThreeSubJettiness = 'jetsThreeSubJettiness', 
    subjetsTrimmingTagged = 'subjetsTrimmingTagged', 
    subjetsTrimming = 'subjetsTrimming', 
    subjetsPruningTagged = 'subjetsPruningTagged', 
    subjetsPruning = 'subjetsPruning', 
    subjetsSoftDropTagged = 'subjetsSoftDropTagged', 
    subjetsSoftDrop = 'subjetsSoftDrop', 

)


from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events

#############################
##   Reco Level Analysis   ##
#############################

from heppy.analyzers.Selector import Selector
# select jet above 400 GeV
fatjets_400 = cfg.Analyzer(
    Selector,
    'fatjets_400',
    output = 'fatjets_400',
    input_objects = 'fatjets',
    filter_func = lambda jet: jet.pt()>400.
)

# produce flat root tree containing jet substructure information
from heppy.analyzers.examples.jetsubstructure.TreeProducer import TreeProducer
tree = cfg.Analyzer(
    TreeProducer,
    fatjets = 'fatjets_400',
)


# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence( [
    source,
    fatjets_400,
    tree,
    ] )


config = cfg.Config(
    components = selectedComponents,
    sequence = sequence,
    services = [],
    events_class = Events
)

if __name__ == '__main__':
    import sys
    from heppy.framework.looper import Looper

    def next():
        loop.process(loop.iEvent+1)

    loop = Looper( 'looper', config,
                   nEvents=100,
                   nPrint=0,
                   timeReport=True)
    loop.process(6)
    print loop.event
