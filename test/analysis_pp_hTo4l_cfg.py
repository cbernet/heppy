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
    files = ['sig.root']
   )
selectedComponents = [comp]

from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    gen_particles = 'genParticles',
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
    photonITags = 'photonITags',
    photonsToITags = 'photonsToITags',

    pfphotons = 'pfphotons',
    pfcharged = 'pfcharged',
    pfneutrals = 'pfneutrals',
    
    met = 'met',
)  

from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events


##################
##   Gen Ana   ##
##################

from heppy.analyzers.Filter import Filter
gen_leptons = cfg.Analyzer(
    Filter,
    'gen_leptons',
    output = 'gen_leptons',
    input_objects = 'gen_particles',
    filter_func = lambda ptc: (abs(ptc.pdgid()) == 11 or (abs(ptc.pdgid()) == 13) ) and ptc.status() == 1
)

from heppy.analyzers.examples.hzz4l.HTo4lGenTreeProducer import HTo4lGenTreeProducer
gen_tree = cfg.Analyzer(
    HTo4lGenTreeProducer,
    leptons = 'gen_leptons',
)

##################
##   Reco Tree   ##
##################

from heppy.analyzers.Filter import Filter
sel_photons = cfg.Analyzer(
    Filter,
    'sel_photons',
    output = 'sel_photons',
    input_objects = 'photons',
    filter_func = lambda ptc: ptc.pt()>2
)

from heppy.analyzers.Merger import Merger
iso_candidates = cfg.Analyzer(
      Merger,
      instance_label = 'iso_candidates', 
      inputs = ['pfphotons','pfcharged','pfneutrals'],
      output = 'iso_candidates'
)

# Compute photon isolation w/r other particles in the event.
from heppy.analyzers.IsolationAnalyzer import IsolationAnalyzer
from heppy.particles.isolation import EtaPhiCircle

iso_photons = cfg.Analyzer(
    IsolationAnalyzer,
    candidates = 'photons',
    particles = 'iso_candidates',
    iso_area = EtaPhiCircle(0.3)
)

sel_iso_photons = cfg.Analyzer(
    Filter,
    'sel_iso_photons',
    output = 'sel_iso_photons',
    input_objects = 'sel_photons',
    filter_func = lambda ptc : ptc.iso.sumpt/ptc.pt()<1.0
)


from heppy.analyzers.Subtractor import Subtractor
pfphotons_nofsr = cfg.Analyzer(
      Subtractor,
      instance_label = 'pfphotons_nofsr', 
      inputA = 'pfphotons',
      inputB = 'sel_iso_photons',
      output = 'pfphotons_nofsr'
)

iso_candidates_nofsr = cfg.Analyzer(
      Merger,
      instance_label = 'iso_candidates_nofsr', 
      inputs = ['pfphotons_nofsr','pfcharged','pfneutrals'],
      output = 'iso_candidates_nofsr'
)

sel_muons = cfg.Analyzer(
    Filter,
    'sel_muons',
    output = 'sel_muons',
    input_objects = 'muons',
    filter_func = lambda ptc: ptc.pt()>5
)

iso_muons = cfg.Analyzer(
    IsolationAnalyzer,
    candidates = 'muons',
    particles = 'iso_candidates_nofsr',
    iso_area = EtaPhiCircle(0.4)
)

sel_iso_muons = cfg.Analyzer(
    Filter,
    'sel_iso_muons',
    output = 'sel_iso_muons',
    input_objects = 'sel_muons',
    filter_func = lambda ptc: ptc.iso.sumpt/ptc.pt()<0.4
)
 
from heppy.analyzers.Dresser import Dresser
dressed_muons = cfg.Analyzer(
    Dresser,
    output = 'dressed_muons',
    particles = 'sel_iso_photons',
    candidates = 'sel_iso_muons',
    area = EtaPhiCircle(0.3)
)


sel_electrons = cfg.Analyzer(
    Filter,
    'sel_electrons',
    output = 'sel_electrons',
    input_objects = 'electrons',
    filter_func = lambda ptc: ptc.pt()>7
)

iso_electrons = cfg.Analyzer(
    IsolationAnalyzer,
    candidates = 'electrons',
    particles = 'iso_candidates_nofsr',
    iso_area = EtaPhiCircle(0.4)
)

sel_iso_electrons = cfg.Analyzer(
    Filter,
    'sel_iso_electrons',
    output = 'sel_iso_electrons',
    input_objects = 'sel_electrons',
    filter_func = lambda ptc: ptc.iso.sumpt/ptc.pt()<0.4
)

dressed_electrons = cfg.Analyzer(
    Dresser,
    output = 'dressed_electrons',
    particles = 'sel_iso_photons',
    candidates = 'sel_iso_electrons',
    area = EtaPhiCircle(0.3)
)

from heppy.analyzers.Merger import Merger
dressed_leptons = cfg.Analyzer(
      Merger,
      instance_label = 'dressed_leptons', 
      inputs = ['dressed_electrons','dressed_muons']
)

from heppy.analyzers.ResonanceBuilder import ResonanceBuilder
zeds_muons = cfg.Analyzer(
      ResonanceBuilder,
      output = 'zeds_muons',
      leg_collection = 'dressed_muons',
      pdgid = 23
)

zeds_electrons = cfg.Analyzer(
      ResonanceBuilder,
      output = 'zeds_electrons',
      leg_collection = 'dressed_electrons',
      pdgid = 23
)

zeds = cfg.Analyzer(
      Merger,
      instance_label = 'zeds',
      inputs = ['zeds_electrons','zeds_muons'],
      output = 'zeds'
)

higgses = cfg.Analyzer(
      ResonanceBuilder,
      output = 'higgses',
      leg_collection = 'zeds',
      pdgid = 25
)


from heppy.analyzers.examples.hzz4l.selection import Selection
selection = cfg.Analyzer(
    Selection,
    instance_label='cuts'
)

from heppy.analyzers.examples.hzz4l.HTo4lTreeProducer import HTo4lTreeProducer
reco_tree = cfg.Analyzer(
    HTo4lTreeProducer,
    zeds = 'zeds',
    higgses = 'higgses',
)


# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence( [
    source,
    gen_leptons,
    gen_tree,
    iso_candidates,
    sel_photons,
    iso_photons,
    sel_iso_photons, 
    pfphotons_nofsr,
    iso_candidates_nofsr,
    sel_muons,
    iso_muons,
    sel_iso_muons,
    dressed_muons,
    sel_electrons,
    iso_electrons,
    sel_iso_electrons,
    dressed_electrons,
    zeds_electrons,
    zeds_muons,
    zeds,
    selection,
    higgses,
    reco_tree,
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
