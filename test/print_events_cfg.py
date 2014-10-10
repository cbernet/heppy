import os
import framework.config as cfg

inputSample = cfg.Component(
    'albers_example',
    files = ['albers.root'],
    )

muana = cfg.Analyzer(
    'LeptonAnalyzer_1',
    id = 4,
    pt = 10.,
    eta = 3.,
    coll_name = 'muons'
    )

eleana = cfg.Analyzer(
    'LeptonAnalyzer_2',
    id = 5,
    pt = 10.,
    eta = 3.,
    coll_name = 'electrons'
    )

jetana = cfg.Analyzer(
    'JetAnalyzer',
    verbose = False
    )

treeprod = cfg.Analyzer(
    'JetTreeProducer',
    tree_name = 'tree',
    tree_title = 'a title'
    )

selectedComponents  = [inputSample]

sequence = cfg.Sequence( [
    muana,
    eleana,
    jetana,
    treeprod
    ] )

config = cfg.Config( components = selectedComponents,
                     sequence = sequence )
