import os
import copy
import heppy.framework.config as cfg

import logging
# next 2 lines necessary to deal with reimports from ipython
logging.shutdown()
reload(logging)
logging.basicConfig(level=logging.WARNING)

comp = cfg.Component(
    'example',
     files = ["root://eospublic.cern.ch//eos/fcc/hh/tutorials/ttbar/ttbar_1.root"]
)
selectedComponents = [comp]

from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,

    #gen_particles = 'genParticles',
    #gen_vertices = 'genVertices',

    gen_jets = 'genJets',

    jets = 'jets',
    bTags = 'bTags',
    cTags = 'cTags',
    tauTags = 'tauTags',

    electrons = 'electrons',
    electronITags = 'electronITags',

    muons = 'muons',
    muonITags = 'muonITags',

    photons = 'photons',
    met = 'met',
)

from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events


#from heppy.analyzers.MyGenAnalyzer import GenAnalyzer
#genana = cfg.Analyzer(
#    GenAnalyzer
#    )



from heppy.analyzers.Selector import Selector
muons = cfg.Analyzer(
    Selector,
    'sel_muons',
    output = 'muons',
    input_objects = 'muons',
    filter_func = lambda ptc: ptc.pt()>30
)

from heppy.analyzers.Selector import Selector
iso_muons = cfg.Analyzer(
    Selector,
    'sel_iso_muons',
    output = 'sel_iso_muons',
    input_objects = 'muons',
    filter_func = lambda ptc: ptc.iso.sumpt/ptc.pt()<0.2
)

from heppy.analyzers.Selector import Selector
electrons = cfg.Analyzer(
    Selector,
    'sel_electrons',
    output = 'electrons',
    input_objects = 'electrons',
    filter_func = lambda ptc: ptc.pt()>30
)

from heppy.analyzers.Selector import Selector
iso_electrons = cfg.Analyzer(
    Selector,
    'sel_iso_electrons',
    output = 'sel_iso_electrons',
    input_objects = 'electrons',
    filter_func = lambda ptc: ptc.iso.sumpt/ptc.pt()<0.1
)


jets_30 = cfg.Analyzer(
    Selector,
    'jets_30',
    output = 'jets_30',
    input_objects = 'jets',
    filter_func = lambda jet: jet.pt()>30.
)

from heppy.analyzers.Matcher import Matcher
match_jet_electrons = cfg.Analyzer(
    Matcher,
    'electron_jets',
    delta_r = 0.2,
    match_particles = 'sel_iso_electrons',
    particles = 'jets_30'
)

sel_jets_electron = cfg.Analyzer(
    Selector,
    'sel_jets_noelecetron_30',
    output = 'sel_jets_noelectron_30',
    input_objects = 'jets_30',
    filter_func = lambda jet: jet.match is None
)


from heppy.analyzers.Matcher import Matcher
match_muon_jets = cfg.Analyzer(
    Matcher,
    'muon_jets',
    delta_r = 0.2,
    match_particles = 'sel_iso_muons',
    particles = 'sel_jets_noelectron_30'
)

sel_jets_muon = cfg.Analyzer(
    Selector,
    'sel_jets_nomuon_30',
    output = 'sel_jets_noelectronnomuon_30',
    input_objects = 'sel_jets_noelectron_30',
    filter_func = lambda jet: jet.match is None
)


from heppy.analyzers.examples.ttbar.BTagging import BTagging
btagging = cfg.Analyzer(
    BTagging,
    'b_jets_30',
    output = 'b_jets_30',
    input_objects = 'sel_jets_noelectronnomuon_30',
    filter_func = lambda jet : jet.tags['bf']>0.
)


from heppy.analyzers.M3Builder import M3Builder
m3 = cfg.Analyzer(
    M3Builder,
    instance_label = 'm3',
    jets = 'sel_jets_noelectronnomuon_30',
    filter_func = lambda x : x.pt()>30.
)

from heppy.analyzers.MTW import MTW
mtw = cfg.Analyzer(
    MTW,
    instance_label = 'mtw',
    met = 'met',
    electron = 'sel_iso_electrons',
    muon = 'sel_iso_muons'
)



from heppy.analyzers.examples.ttbar.selection import Selection
selection = cfg.Analyzer(
    Selection,
    instance_label='cuts'
)

from heppy.analyzers.examples.ttbar.TTbarTreeProducer import TTbarTreeProducer
gen_tree = cfg.Analyzer(
    TTbarTreeProducer,
    jets_30 = 'sel_jets_noelectronnomuon_30',
    m3 = 'm3',
    met = 'met',
    mtw= 'mtw',
    muons = 'sel_iso_muons',
    electrons = 'sel_iso_electrons'
)


# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence( [
    source,
    jets_30,
    muons,
    electrons,
    iso_muons,
    iso_electrons,
    match_jet_electrons,
    sel_jets_electron,
    match_muon_jets,
    sel_jets_muon,
    btagging,
    selection,
    m3, 
    mtw,
    #genana,

    gen_tree
    ] )

# comp.files.append('example_2.root')
#comp.splitFactor = len(comp.files)  # splitting the component in 2 chunks

config = cfg.Config(
    components = selectedComponents,
    sequence = sequence,
    services = [],
    events_class = Events
)

if __name__ == '__main__':
    import sys
    from heppy.framework.looper import Looper

    def next():
        loop.process(loop.iEvent+1)

    loop = Looper( 'looper', config,
                   nEvents=100,
                   nPrint=0,
                   timeReport=True)
    loop.process(6)
    print loop.event
