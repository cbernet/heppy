
import framework.Config as cfg

dummyInputSample = cfg.Component(
    'Test',
    files = []
    )

printer = cfg.Analyzer(
    'Printer'
    )



selectedComponents  = [dummyInputSample]

sequence = cfg.Sequence( [
    printer
    ] )

config = cfg.Config( components = selectedComponents,
                     sequence = sequence )
