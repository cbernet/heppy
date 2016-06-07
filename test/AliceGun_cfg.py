import os
import copy
import heppy.framework.config as cfg

import logging
import  math



logging.basicConfig(level=logging.WARNING)

# setting the random seed for reproducible results
#import heppy.papas.random as  random
from heppy.statistics.rrandom import RRandom as random
random.seed(0xdeadbeef)

make_tree = True

comp = cfg.Component(
    'example',
    # files = 'example.root'
    files = [None]
)
selectedComponents = [comp]

from heppy.analyzers.AliceTestGun import Gun
source = cfg.Analyzer(
    Gun,
    pdgid = 211,
    thetamin = -1.5,
    thetamax = 1.5,
    ptmin = 0.1,
    ptmax = 10,
    flat_pt = True,
)

#from heppy.analyzers.AliceTestGun import Gun
#source = cfg.Analyzer(
    #Gun,
    #pdgid = 22,
    #thetamin = -1.5,
    #thetamax = 1.5,
    #ptmin = 0.1,
    #ptmax = 10,
    #flat_pt = True,
#)

#from heppy.analyzers.AliceTestGun import Gun
#source = cfg.Analyzer(
    #Gun,
    #pdgid = 130,
    #thetamin = -1.5,
    #thetamax = 1.5,
    #ptmin = 0.1,
    #ptmax = 10,
    #flat_pt = True,
#)

#from heppy.analyzers.AliceTestGun import Gun
#source = cfg.Analyzer(
    #Gun,
    #pdgid = 211,
    #theta = 0.9, 
    #phi = -0.19, 
    #energy = 47.2
#)


#from heppy.analyzers.Papas import Papas
#from heppy.papas.detectors.CMS import CMS
#papas = cfg.Analyzer(
    #Papas,
    #instance_label = 'papas',
    #detector = CMS(),
    #gen_particles = 'gen_particles_stable',
    #sim_particles = 'sim_particles',
    #rec_particles = 'particles',
    #display = False,
    #verbose = True
#)


from heppy.analyzers.PapasSim import PapasSim
from heppy.analyzers.Papas import Papas
from heppy.papas.detectors.CMS import CMS
papas = cfg.Analyzer(
    PapasSim,
    instance_label = 'papas',
    detector = CMS(),
    gen_particles = 'gen_particles_stable',
    sim_particles = 'sim_particles',
    merged_ecals = 'ecal_clusters',
    merged_hcals = 'hcal_clusters',
    tracks = 'tracks', 
    output_history = 'history_nodes', 
    display_filter_func = lambda ptc: ptc.e()>1.,
    display = False,
    verbose = True
)


# group the clusters, tracks from simulation into connected blocks ready for reconstruction
from heppy.analyzers.PapasPFBlockBuilder import PapasPFBlockBuilder
pfblocks = cfg.Analyzer(
    PapasPFBlockBuilder,
    tracks = 'tracks', 
    ecals = 'ecal_clusters', 
    hcals = 'hcal_clusters', 
    history = 'history_nodes',  
    output_blocks = 'reconstruction_blocks'
)

#reconstruct particles from blocks
from heppy.analyzers.PapasPFReconstructor import PapasPFReconstructor
pfreconstruct = cfg.Analyzer(
    PapasPFReconstructor,
    instance_label = 'papas_PFreconstruction', 
    detector = CMS(),
    input_blocks = 'reconstruction_blocks',
    history = 'history_nodes',     
    output_particles_dict = 'particles_dict', 
    output_particles_list = 'particles_list'
)

# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence( [
    source,
    papas,
    pfblocks,
    pfreconstruct
    ] )



from ROOT import gSystem
from heppy.framework.eventsgen import Events

config = cfg.Config(
    components = selectedComponents,
    sequence = sequence,
    services = [],
    events_class = Events
)

if __name__ == '__main__':
    import sys
    from heppy.framework.looper import Looper

    def process(iev=None):
        if iev is None:
            iev = loop.iEvent
        loop.process(iev)
        loop.write()
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
        for j in range(10) :
            process(iev)
        pass
        #process(iev) #alice_debug
        #process(iev) #alice_debug
        #process(iev) #alice_debug
    else:
        loop.loop()
        loop.write()
