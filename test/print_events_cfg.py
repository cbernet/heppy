import os
import framework.config as cfg

inputSample = cfg.Component(
    'NameThatYouCanChoose',
    files = ['albers.root'],
    tree_name = 'events'
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
