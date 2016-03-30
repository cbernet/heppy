import os
import copy
import heppy.framework.config as cfg

import logging

#import sys
# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)
logging.basicConfig(level=logging.WARNING)

comp = cfg.Component(
    'example',
    files = [
        'ee_ZH_Zmumu_Hbb.root'
    ]
)
selectedComponents = [comp]

from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    mode = 'ee',
    gen_particles = 'GenParticle',
)

# Use a Filter to select stable gen particles for simulation
# from the output of "source" 
# help(Filter) for more information
from heppy.analyzers.Filter import Filter
gen_particles_stable = cfg.Analyzer(
    Filter,
    output = 'gen_particles_stable',
    # output = 'particles',
    input_objects = 'gen_particles',
    filter_func = lambda x : x.status()==1 and x.pdgid() not in [12,14,16] and x.pt()>0.1
)

from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events
#from heppy.framework.eventsgen import Events

from heppy.papas.aliceproto.PapasSim import PapasSim
from heppy.papas.detectors.CMS import CMS
papas = cfg.Analyzer(
    PapasSim,
    instance_label = 'papas',
    detector = CMS(),
    gen_particles = 'gen_particles_stable',
    sim_particles = 'sim_particles',
    rec_particles = 'rec_particles',
    display_filter_func = lambda ptc: ptc.e()>1.,
    display = False,
    verbose = True
)

from heppy.analyzers.PapasPFBlockBuilder import PapasPFBlockBuilder
pfblocks = cfg.Analyzer(
    PapasPFBlockBuilder
)


from heppy.papas.aliceproto.PapasPFReconstructor import PapasPFReconstructor
pfreconstruct = cfg.Analyzer(
    PapasPFReconstructor
)

from heppy.papas.aliceproto.PapasParticlesComparer import PapasParticlesComparer 
particlescomparer = cfg.Analyzer(
    PapasParticlesComparer 
)

# and then particle reconstruction from blocks 

# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence( [
    source,
    gen_particles_stable,
    papas,
    pfblocks,
    pfreconstruct,
    particlescomparer
    ] )
 
config = cfg.Config(
    components = selectedComponents,
    sequence = sequence,
    services = [],
    events_class = Events
)




if __name__ == '__main__':
    import sys
    from heppy.framework.looper import Looper

    import random
    random.seed(0xdeadbeef)

    def process(iev=None):
        if iev is None:
            iev = loop.iEvent
        loop.process(iev)
        if display:
            display.draw()

    def next():
        loop.process(loop.iEvent+1)
        if display:
            display.draw()            

    iev = None
    if len(sys.argv)==2:
        papas.display = True
        iev = int(sys.argv[1])
       
    loop = Looper( 'looper', config,
                   nEvents=1000,
                   nPrint=0,
                   firstEvent=0,
                   timeReport=True)
    simulation = None
    for ana in loop.analyzers: 
        if hasattr(ana, 'display'):
            simulation = ana
    display = getattr(simulation, 'display', None)
    simulator = getattr(simulation, 'simulator', None)
    
    if simulator: 
        detector = simulator.detector
    if iev is not None:
        for j in range(10000) :
            process(iev)
            process(iev) #alice_debug
            process(iev) #alice_debug
            process(iev) #alice_debug
    else:
        loop.loop()
        loop.write()
