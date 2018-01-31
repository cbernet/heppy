'''Example configuration file showing how to read LCIO events.
Use it in Lyon: 
 source /gridsoft/ipnls/ilc/v01-17-09/init_ilcsoft.sh

 heppy_loop.py Output lcio_cfg.py
'''


import os
import heppy.framework.config as cfg
from heppy.framework.eventslcio import Events
import logging
logging.basicConfig(level=logging.INFO)


inputSample = cfg.Component(
    'test_component',
    files = '/gridgroup/ilc/kurca/simple_lcio.slcio',
    )

from heppy.analyzers.lcio.MCParticlePrinter import MCParticlePrinter
mc_ptc_printer = cfg.Analyzer(
    MCParticlePrinter
)

selectedComponents  = [inputSample]



# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence( [
        mc_ptc_printer
] )


# finalization of the configuration object. 
config = cfg.Config( components = selectedComponents,
                     sequence = sequence,
                     services = [], 
                     events_class = Events )


