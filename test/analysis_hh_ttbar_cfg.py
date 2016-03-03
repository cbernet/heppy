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
    #files = ['example.root']
    files = ['/afs/cern.ch/user/d/drasal/public/delphes/FCCDelphesOutput_1.root',
             '/afs/cern.ch/user/d/drasal/public/delphes/FCCDelphesOutput_2.root',
             '/afs/cern.ch/user/d/drasal/public/delphes/FCCDelphesOutput_3.root',
             '/afs/cern.ch/user/d/drasal/public/delphes/FCCDelphesOutput_4.root',
             '/afs/cern.ch/user/d/drasal/public/delphes/FCCDelphesOutput_5.root',
             '/afs/cern.ch/user/d/drasal/public/delphes/FCCDelphesOutput_6.root',
             '/afs/cern.ch/user/d/drasal/public/delphes/FCCDelphesOutput_7.root',
             '/afs/cern.ch/user/d/drasal/public/delphes/FCCDelphesOutput_8.root',
             '/afs/cern.ch/user/d/drasal/public/delphes/FCCDelphesOutput_9.root',
             '/afs/cern.ch/user/d/drasal/public/delphes/FCCDelphesOutput_10.root',
]
    #files = ['FCCDelphes_ClementOutput1.root']
)
selectedComponents = [comp]

from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    mode = 'pp',
    #gen_particles = 'genParticles',
    gen_jets = 'genJets',

    jets = 'jets',
    bTags = 'bTags',
    jetsToBTags = 'jetsToBTags',

    electrons = 'electrons',
    electronITags = 'electronITags',
    electronsToITags = 'electronsToITags',

    muons = 'muons',
    muonITags = 'muonITags',
    muonsToITags = 'muonsToITags',

    photons = 'photons',
    met = 'met',
)  

from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events



from heppy.analyzers.Filter import Filter
muons = cfg.Analyzer(
    Filter,
    'sel_muons',
    output = 'muons',
    input_objects = 'muons',
    filter_func = lambda ptc: ptc.pt()>30
)

from heppy.analyzers.Filter import Filter
iso_muons = cfg.Analyzer(
    Filter,
    'sel_iso_muons',
    output = 'sel_iso_muons',
    input_objects = 'muons',
    filter_func = lambda ptc: ptc.iso.sumpt/ptc.pt()<0.5
)

from heppy.analyzers.Filter import Filter
electrons = cfg.Analyzer(
    Filter,
    'sel_electrons',
    output = 'electrons',
    input_objects = 'electrons',
    filter_func = lambda ptc: ptc.pt()>30
)

from heppy.analyzers.Filter import Filter
iso_electrons = cfg.Analyzer(
    Filter,
    'sel_iso_electrons',
    output = 'sel_iso_electrons',
    input_objects = 'electrons',
    filter_func = lambda ptc: ptc.iso.sumpt/ptc.pt()<0.5
)


jets_30 = cfg.Analyzer(
    Filter,
    'jets_30',
    output = 'jets_30',
    input_objects = 'jets',
    filter_func = lambda jet: jet.pt()>30.
)

from heppy.analyzers.Matcher import Matcher
match_jet_electrons = cfg.Analyzer(
    Matcher,
    delta_r = 0.4,
    match_particles = 'sel_iso_electrons',
    particles = 'jets_30'
)

sel_jets_electron = cfg.Analyzer(
    Filter,
    'sel_jets_noelecetron_30',
    output = 'sel_jets_noelectron_30',
    input_objects = 'jets_30',
    filter_func = lambda jet: jet.match is None
)


from heppy.analyzers.Matcher import Matcher
match_muon_jets = cfg.Analyzer(
    Matcher,
    delta_r = 0.4,
    match_particles = 'sel_jets_noelectron_30',
    particles = 'sel_iso_muons'
)

sel_muons_jet = cfg.Analyzer(
    Filter,
    'sel_iso_muons_nojets_30',
    output = 'sel_iso_muons_nojets_30',
    input_objects = 'sel_iso_muons',
    filter_func = lambda muon: muon.match is None
)


from heppy.analyzers.Btagging import Btagging
btagging = cfg.Analyzer(
    Btagging,
    'b_jets_30',
    output = 'b_jets_30',
    input_objects = 'sel_jets_noelectron_30',
    filter_func = lambda jet : jet.tags['bf']>0.
)


from heppy.analyzers.M3Builder import M3Builder
m3 = cfg.Analyzer(
    M3Builder,
    instance_label = 'm3',
    jets = 'sel_jets_noelectron_30', 
    filter_func = lambda x : x.pt()>35.
)

from heppy.analyzers.MTW import MTW
mtw = cfg.Analyzer(
    MTW,
    instance_label = 'mtw',
    met = 'met',
    electron = 'sel_iso_electrons',
    muon = 'sel_iso_muons_nojets_30'
)



from heppy.analyzers.examples.ttbar.selection import Selection
selection = cfg.Analyzer(
    Selection,
    instance_label='cuts'
)

from heppy.analyzers.examples.ttbar.TTbarTreeProducer import TTbarTreeProducer
gen_tree = cfg.Analyzer(
    TTbarTreeProducer,
    jets_30 = 'sel_jets_noelectron_30',
    m3 = 'm3',
    met = 'met',
    mtw= 'mtw',
    muons = 'sel_iso_muons_nojets_30',
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
    sel_muons_jet,
    btagging,
    selection,
    m3, 
    mtw,
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
