import os
import framework.config as cfg

# input component 
# several input components can be declared,
# and added to the list of selected components
inputSample = cfg.Component(
    'albers_example',
    files = ['albers.root'],
    )

selectedComponents  = [inputSample]

# analyzers

# lepton analyzer for muons (type 4)
muana = cfg.Analyzer(
    'LeptonAnalyzer_1',
    id = 4,   # selected particle id
    pt = 10., # pt cut
    eta = 3., # eta cut 
    coll_name = 'muons' # will create a list of leptons with this name in the event
    )

# lepton analyzer for electrons
eleana = cfg.Analyzer(
    'LeptonAnalyzer_2',
    id = 5,
    pt = 10.,
    eta = 3.,
    coll_name = 'electrons'
    )

# jet analyzer
jetana = cfg.Analyzer(
    'JetAnalyzer',
    verbose = False
    )

# analyzer for tree production
treeprod = cfg.Analyzer(
    'JetTreeProducer',
    tree_name = 'tree',
    tree_title = 'a title'
    )

# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence( [
    muana,
    eleana,
    jetana,
    treeprod
    ] )

# finalization of the configuration object. 
config = cfg.Config( components = selectedComponents,
                     sequence = sequence )
