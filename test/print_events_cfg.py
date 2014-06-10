import os
import framework.config as cfg

inputSample = cfg.Component(
    'NameThatYouCanChoose',
    files = ['test_tree.root'],
    tree_name = 'test_tree'
    )

printer = cfg.Analyzer(
    'Printer'
    )

selectedComponents  = [inputSample]

sequence = cfg.Sequence( [
    printer
    ] )

config = cfg.Config( components = selectedComponents,
                     sequence = sequence )
