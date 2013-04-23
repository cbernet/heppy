
import framework.Config as cfg

dummyInputSample = cfg.Component(
    'Test',
    files = []
    )

dummyAna = cfg.Analyzer(
    'Analyzer'
    )


selectedComponents  = [dummyInputSample] 

sequence = cfg.Sequence( [
    dummyAna
    ] )

config = cfg.Config( components = selectedComponents,
                     sequence = sequence )

