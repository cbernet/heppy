'''Example configuration file a particle gun in heppy, with the FCC-ee

While studying this file, open it in ipython as well as in your editor to 
get more information: 

ipython
from gun_papas_cfg import * 
'''

import os
import copy
import heppy.framework.config as cfg

import logging

# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)


# global logging level for the heppy framework.
# in addition, all the analyzers declared below have their own logger,
# an each of them can be set to a different logging level.
logging.basicConfig(level=logging.WARNING)

# setting the random seed for reproducible results
import heppy.statistics.rrandom as random
# do not forget to comment out the following line if you want to produce and combine
# several samples of events 
random.seed(0xdeadbeef)

# loading the FCC event data model library to decode
# the format of the events in the input file
# help(Events) for more information 
from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events

# setting the event printout
# help(Event) for more information
from heppy.framework.event import Event
# comment the following line to see all the collections stored in the event 
# if collection is listed then print loop.event.papasevent will include the collections
Event.print_patterns=['zeds*', 'higgs*', 'rec_particles', 'gen_particles_stable', 'recoil*', 'collections']

# definition of the collider
# help(Collider) for more information
from heppy.configuration import Collider
Collider.BEAMS = 'ee'
Collider.SQRTS = 240.

pdgid = [211, 130]

# dummy input component (we use a particle gun)
comp = cfg.Component(
    'gun_{}'.format(pdgid),
    files = [None]
)


from heppy.analyzers.PapasDagPlotter import PapasDAGPlotter
papas_dag_plot= cfg.Analyzer(
    PapasDAGPlotter,
    plottype = "dag_event",
    show_file = False
)

# selecting the list of components to be processed. Here only one. 
selectedComponents = [comp]

# particle gun analyzer
import math
from heppy.analyzers.Gun import Gun
source = cfg.Analyzer(
    Gun,
    pdgid = pdgid,
    thetamin = -0.1,
    thetamax = 0.1,
    phimin = math.pi/2.,
    phimax = math.pi/2.,
    ptmin = 5,
    ptmax = 10,
    flat_pt = False,
    papas = True
)

# importing the papas simulation and reconstruction sequence,
# as well as the detector used in papas
# check papas_cfg.py for more information
from heppy.test.papas_cfg import papas, papas_sequence, detector, papasdisplay, papasdisplaycompare

from jet_tree_cff import jet_tree_sequence

from heppy.analyzers.P4SumBuilder import P4SumBuilder
sum_particles = cfg.Analyzer(
    P4SumBuilder, 
    output='sum_all_ptcs',
    #    particles='gen_particles_stable'
    particles='rec_particles'
)

sum_gen = cfg.Analyzer(
    P4SumBuilder, 
    output='sum_all_gen',
    particles='gen_particles_stable'
)


from heppy.analyzers.GlobalEventTreeProducer import GlobalEventTreeProducer
zed_tree = cfg.Analyzer(
    GlobalEventTreeProducer, 
    sum_all='sum_all_ptcs', 
    sum_all_gen='sum_all_gen'
)

# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence(
    source, 
    papas_sequence,
#    jet_tree_sequence('gen_particles_stable','rec_particles',
#    njets=None, ptmin=0.5),
#    sum_particles,
#    sum_gen,
#    zed_tree
)

# Specifics for particle gun events
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
    import heppy.statistics.rrandom as random
    from heppy.papas.data.identifier import Identifier
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
    usage = '''usage: python analysis_ee_ZH_cfg.py [ievent]
    
    Provide ievent as an integer, or loop on the first events.
    You can also use this configuration file in this way: 
    
    heppy_loop.py OutDir/ analysis_ee_ZH_cfg.py -f -N 100 
    '''
    if len(sys.argv)==2:
        papasdisplay.display = True
        papasdisplaycompare.display = True
        try:
            iev = int(sys.argv[1])
        except ValueError:
            print usage
            sys.exit(1)
    elif len(sys.argv)>2: 
        print usage
        sys.exit(1)
            
    loop = Looper( 'looper', config,
                   nEvents=10,
                   nPrint=1,
                   timeReport=True)
    
    for ana in loop.analyzers: 
        if hasattr(ana, 'display'):
            display = getattr(ana, 'display', None)
    
    if iev is not None:
        process(iev)
        pass
    else:
        loop.loop()
        loop.write()
