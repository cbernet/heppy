import os
from framework.chain import Chain
import framework.Config as cfg

dummyInputSample = cfg.Component(
    'TestSample',
    files = ['test_tree.root']
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