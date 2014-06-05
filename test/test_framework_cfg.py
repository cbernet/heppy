import os
from framework.chain import Chain
import framework.config as cfg

dummyInputSample = cfg.Component(
    'TestSample',
    files = ['test_tree.root'],
    tree_name = 'test_tree'
    )

gun = cfg.Analyzer(
    'ParticleGun'
    )

printer = cfg.Analyzer(
    'Printer'
    )


selectedComponents  = [dummyInputSample]

sequence = cfg.Sequence( [
    gun,
    printer
    ] )

config = cfg.Config( components = selectedComponents,
                     sequence = sequence )

#TODO illustrate the use of Counter
#TODO illustrate the use of
