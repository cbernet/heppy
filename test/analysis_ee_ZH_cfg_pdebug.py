'''Example configuration file for an ee->ZH->mumubb analysis in heppy, with the FCC-ee

While studying this file, open it in ipython as well as in your editor to 
get more information: 

ipython
from analysis_ee_ZH_cfg import * 

'''

import os
import copy
import heppy.framework.config as cfg
from heppy.utils.pdebug import pdebugger

import logging
# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)
logging.basicConfig(level=logging.WARNING)
#logging.basicConfig(level=logging.INFO)
# setting the random seed for reproducible results
#import random
from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events
import heppy.statistics.rrandom as random
random.seed(0xdeadbeef)

# input definition
comp = cfg.Component(
    'example',
    files = [
            '/Users/alice/fcc/pythiafiles/ee_ZH_Zmumu_Hbb.root'
        ]    
)
selectedComponents = [comp]

# read FCC EDM events from the input root file(s)
# do help(Reader) for more information
from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    mode = 'ee',
    gen_particles = 'GenParticle',
    gen_vertices = 'GenVertex'
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
    filter_func = lambda x : x.status()==1 and abs(x.pdgid()) not in [12,14,16] and x.pt()>1e-5  
)

# configure the papas fast simulation with the CMS detector
# help(Papas) for more information
# history nodes keeps track of which particles produced which tracks, clusters 
from heppy.analyzers.PapasSim import PapasSim
#from heppy.analyzers.Papas import Papas
from heppy.papas.detectors.CMS import CMS
papas = cfg.Analyzer(
    PapasSim,
    instance_label = 'papas',
    detector = CMS(),
    gen_particles = 'gen_particles_stable',
    sim_particles = 'sim_particles',
    sim_ecals='sim_ecal_clusters',
    sim_hcals='sim_ecal_clusters',
    smeared_ecals = 'smeared_ecal_clusters',
    smeared_hcals = 'smeared_hcal_clusters',    
    merged_ecals = 'merged_ecal_clusters',
    merged_hcals = 'merged_hcal_clusters',
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

from heppy.analyzers.PapasHistory import PapasHistory
papashistory = cfg.Analyzer(
    PapasHistory,
    instance_label = 'papas_history', 
    detector = CMS(),
    history = 'history'
)


# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence(
    source,
    gen_particles_stable,
    papas,
    pfblocks,
    pfreconstruct,
    papashistory
     )


# Specifics to read FCC events 
from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events

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
    #pdebug.open("/Users/alice/work/Outputs/pythonphysics.txt")

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
    usage = '''usage: python analysis_ee_ZH_cfg.py [ievent]
    
    Provide ievent as an integer, or loop on the first events.
    You can also use this configuration file in this way: 
    
    heppy_loop.py OutDir/ analysis_ee_ZH_cfg.py -f -N 100 
    '''
    if len(sys.argv)==2:
        papas.display = True
        try:
            iev = int(sys.argv[1])
        except ValueError:
            print usage
            sys.exit(1)
    elif len(sys.argv)>2: 
        print usage
        sys.exit(1)
            
        
    loop = Looper( 'looper', config,
                   nEvents=100,
                   nPrint=1,
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
        pdebugger.info(str('Event: {}\n'.format(iev)))
        process(iev)
        process(iev)
        process(iev)
    else:
        loop.loop()
        loop.write()
