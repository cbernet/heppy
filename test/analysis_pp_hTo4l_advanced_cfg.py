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
    files = ['FCCDelphesOutput.root']
   )
selectedComponents = [comp]

from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    gen_particles = 'genParticles',
    gen_jets = 'genJets',

    jets = 'jets',
    bTags = 'bTags',

    electrons = 'electrons',
    electronITags = 'electronITags',

    muons = 'muons',
    muonsToMC = 'muonsToMC',
    muonITags = 'muonITags',

    photons = 'photons',
    photonITags = 'photonITags',

    pfphotons = 'pfphotons',
    pfcharged = 'pfcharged',
    pfneutrals = 'pfneutrals',

    met = 'met',
)

from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events


#############################
##   Gen Level Analysis    ##
#############################

# select stable electrons and muons
from heppy.analyzers.Selector import Selector
gen_leptons = cfg.Analyzer(
    Selector,
    'gen_leptons',
    output = 'gen_leptons',
    input_objects = 'gen_particles',
    filter_func = lambda ptc: (abs(ptc.pdgid()) == 11 or (abs(ptc.pdgid()) == 13) ) and ptc.status() == 1
)

# produce flat root tree containing information about stable leptons in the event
from heppy.analyzers.examples.hzz4l.HTo4lGenTreeProducer import HTo4lGenTreeProducer
gen_tree = cfg.Analyzer(
    HTo4lGenTreeProducer,
    leptons = 'gen_leptons',
)

#############################
##   Reco Level Analysis   ##
#############################

# select fsr photon candidates
from heppy.analyzers.Selector import Selector
sel_photons = cfg.Analyzer(
    Selector,
    'sel_photons',
    output = 'sel_photons',
    input_objects = 'photons',
    filter_func = lambda ptc: ptc.pt()>2
)

# produce particle collection to be used for fsr photon isolation
from heppy.analyzers.Merger import Merger
iso_candidates = cfg.Analyzer(
      Merger,
      instance_label = 'iso_candidates', 
      inputs = ['pfphotons','pfcharged','pfneutrals'],
      output = 'iso_candidates'
)

# compute fsr photon isolation w/r other particles in the event.
from heppy.analyzers.IsolationAnalyzer import IsolationAnalyzer
from heppy.particles.isolation import EtaPhiCircle

iso_photons = cfg.Analyzer(
    IsolationAnalyzer,
    candidates = 'photons',
    particles = 'iso_candidates',
    iso_area = EtaPhiCircle(0.3)
)

# select isolated photons
sel_iso_photons = cfg.Analyzer(
    Selector,
    'sel_iso_photons',
    output = 'sel_iso_photons',
    input_objects = 'sel_photons',
    filter_func = lambda ptc : ptc.iso.sumpt/ptc.pt()<1.0
)

# remove fsr photons from particle-flow photon collections
from heppy.analyzers.Subtractor import Subtractor
pfphotons_nofsr = cfg.Analyzer(
      Subtractor,
      instance_label = 'pfphotons_nofsr', 
      inputA = 'pfphotons',
      inputB = 'sel_iso_photons',
      output = 'pfphotons_nofsr'
)

# produce particle collection to be used for lepton isolation
iso_candidates_nofsr = cfg.Analyzer(
      Merger,
      instance_label = 'iso_candidates_nofsr', 
      inputs = ['pfphotons_nofsr','pfcharged','pfneutrals'],
      output = 'iso_candidates_nofsr'
)

# select muons with pT > 5 GeV
sel_muons = cfg.Analyzer(
    Selector,
    'sel_muons',
    output = 'sel_muons',
    input_objects = 'muons',
    filter_func = lambda ptc: ptc.pt()>5
)

# compute muon isolation 
iso_muons = cfg.Analyzer(
    IsolationAnalyzer,
    candidates = 'muons',
    particles = 'iso_candidates_nofsr',
    iso_area = EtaPhiCircle(0.4)
)

# select isolated muons
sel_iso_muons = cfg.Analyzer(
    Selector,
    'sel_iso_muons',
    output = 'sel_iso_muons',
    input_objects = 'sel_muons',
    filter_func = lambda ptc: ptc.iso.sumpt/ptc.pt()<0.4
)
 
# "dress" muons with fsr photons
from heppy.analyzers.LeptonFsrDresser import LeptonFsrDresser
dressed_muons = cfg.Analyzer(
    LeptonFsrDresser,
    output = 'dressed_muons',
    particles = 'sel_iso_photons',
    leptons = 'sel_iso_muons',
    area = EtaPhiCircle(0.3)
)

# select electrons with pT > 7 GeV
sel_electrons = cfg.Analyzer(
    Selector,
    'sel_electrons',
    output = 'sel_electrons',
    input_objects = 'electrons',
    filter_func = lambda ptc: ptc.pt()>7
)

# compute electron isolation 
iso_electrons = cfg.Analyzer(
    IsolationAnalyzer,
    candidates = 'electrons',
    particles = 'iso_candidates_nofsr',
    iso_area = EtaPhiCircle(0.4)
)

# select isolated electrons
sel_iso_electrons = cfg.Analyzer(
    Selector,
    'sel_iso_electrons',
    output = 'sel_iso_electrons',
    input_objects = 'sel_electrons',
    filter_func = lambda ptc: ptc.iso.sumpt/ptc.pt()<0.4
)

# "dress" electrons with fsr photons
dressed_electrons = cfg.Analyzer(
    LeptonFsrDresser,
    output = 'dressed_electrons',
    particles = 'sel_iso_photons',
    leptons = 'sel_iso_electrons',
    area = EtaPhiCircle(0.3)
)

# merge electrons and muons into a single lepton collection
from heppy.analyzers.Merger import Merger
dressed_leptons = cfg.Analyzer(
      Merger,
      instance_label = 'dressed_leptons', 
      inputs = ['dressed_electrons','dressed_muons'],
      output = 'dressed_leptons'
)

# create Z boson candidates with leptons
from heppy.analyzers.LeptonicZedBuilder import LeptonicZedBuilder
zeds = cfg.Analyzer(
      LeptonicZedBuilder,
      output = 'zeds',
      leptons = 'dressed_leptons',
)

# create H boson candidates
from heppy.analyzers.ResonanceBuilder import ResonanceBuilder
higgses = cfg.Analyzer(
      ResonanceBuilder,
      output = 'higgses',
      leg_collection = 'zeds',
      pdgid = 25
)


# apply event selection. Defined in "analyzers/examples/hzz4l/selection.py"
from heppy.analyzers.examples.hzz4l.selection import Selection
selection = cfg.Analyzer(
    Selection,
    instance_label='cuts'
)

# store interesting quantities into flat ROOT tree
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
    dressed_leptons,
    zeds,
    selection,
    higgses,
    reco_tree,
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

    def next():
        loop.process(loop.iEvent+1)

    loop = Looper( 'looper', config,
                   nEvents=100,
                   nPrint=0,
                   timeReport=True)
    loop.process(6)
    print loop.event
