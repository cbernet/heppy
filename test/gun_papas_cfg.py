'''Example configuration file for an ee->ZH->mumubb analysis in heppy, with the FCC-ee

While studying this file, open it in ipython as well as in your editor to 
get more information: 

ipython
from analysis_ee_ZH_cfg import * 
'''

import os
import copy
import heppy.framework.config as cfg

from heppy.framework.event import Event
Event.print_patterns=['*']

import logging
# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)
logging.basicConfig(level=logging.WARNING)

# setting the random seed for reproducible results
import heppy.statistics.rrandom as random
random.seed(0xdeadbeef)

from heppy.analyzers.Gun import Gun
source = cfg.Analyzer(
    Gun,
    pdgid = 211,
    thetamin = -1.5,
    thetamax = 1.5,
    ptmin = 0,
    ptmax = 100,
    flat_pt = False,
    papas = True
)

comp = cfg.Component(
    'gun_{}'.format(source.pdgid),
    files = [None]
)
selectedComponents = [comp]

from heppy.test.papas_cfg import papas_sequence, detector, papas


from heppy.analyzers.PapasHistoryPrinter import PapasHistoryPrinter
papas_print_history = cfg.Analyzer(
    PapasHistoryPrinter,
    format = "subgroups",
    num_subgroups = 3 # biggest 3 subgroups will be printed
)


from heppy.analyzers.PapasHistoryPrinter import PapasHistoryPrinter
papas_print_history_event = cfg.Analyzer(
    PapasHistoryPrinter,
    format = "event"
)

from heppy.analyzers.PapasDisplay import PapasDisplay 
papasdisplaycompare = cfg.Analyzer(
    PapasDisplay,
    projections = ['xy', 'yz'],
    screennames = ["simulated", "reconstructed"],
    particles_type_and_subtypes = ['ps', 'pr'],
    clusters_type_and_subtypes = [['es', 'hs'],['em', 'hm']],
    detector = detector,
    #save = True,
    display = True
)


from heppy.analyzers.PapasDagPlotter import PapasDAGPlotter
papas_dag_plot= cfg.Analyzer(
    PapasDAGPlotter,
    plottype = "dag_event",
    show_file = False
)

from heppy.analyzers.PapasDagPlotter import PapasDAGPlotter
papas_dag_subgroups= cfg.Analyzer(
    PapasDAGPlotter,
    plottype = "dag_subgroups",
    show_file = False,
    num_subgroups = 4
)


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
    #papas_history,
    papas_print_history, 
    papasdisplaycompare,
    #papas_print_history_event, 
    papas_dag_plot,
    #papas_dag_subgroups,     
    jet_tree_sequence('gen_particles_stable','rec_particles',
                  njets=None, ptmin=0.5),
    sum_particles,
    sum_gen,
    zed_tree
    )

# Specifics to read FCC events 
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
                   nEvents=1000,
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
        process(iev)
        pass       
    else:
        loop.loop()
        loop.write()
