import framework.Config as cfg

dummyInputSample = cfg.Component(
    'Test'
    files = []
    )


selectedComponents  = [dummyInputSample] 

sequence = cfg.Sequence( [
    ] )

config = cfg.Config( components = selectedComponents,
                     sequence = sequence )

