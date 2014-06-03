
import framework.Config as cfg

dummyInputSample = cfg.Component(
    'Test',
    files = []
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
