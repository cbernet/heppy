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

from heppy.analyzers.Filter import Filter
photons = cfg.Analyzer(
    Filter,
    'sel_photons',
    output = 'photons',
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
    leptons = 'photons',
    particles = 'iso_candidates',
    iso_area = EtaPhiCircle(0.3)
)

# one can pass a function like this one to the filter:
def relative_isolation(photon):
    sumpt = photon.iso_211.sumpt + photon.iso_130.sumpt
    sumpt /= photon.pt()
    return sumpt
# ... or use a lambda statement as done below. 


sel_iso_photons = cfg.Analyzer(
    Filter,
    'sel_iso_photons',
    output = 'sel_iso_photons',
    input_objects = 'photons_true',
    # filter_func = relative_isolation
    filter_func = lambda lep : lep.iso.sumpt/lep.pt()<1.0
)

muons = cfg.Analyzer(
    Filter,
    'sel_muons',
    output = 'muons',
    input_objects = 'muons',
    filter_func = lambda ptc: ptc.pt()>5
)

iso_muons = cfg.Analyzer(
    Filter,
    'iso_muons',
    output = 'iso_muons',
    input_objects = 'muons',
    filter_func = lambda ptc: ptc.iso.sumpt/ptc.pt()<0.4
)

electrons = cfg.Analyzer(
    Filter,
    'sel_electrons',
    output = 'electrons',
    input_objects = 'electrons',
    filter_func = lambda ptc: ptc.pt()>7
)

iso_electrons = cfg.Analyzer(
    Filter,
    'iso_electrons',
    output = 'iso_electrons',
    input_objects = 'electrons',
    filter_func = lambda ptc: ptc.iso.sumpt/ptc.pt()<0.4
)


from heppy.analyzers.Merger import Merger
iso_leptons = cfg.Analyzer(
      Merger,
      instance_label = 'merge_leptons', 
      inputs = ['iso_electrons','iso_muons']
      inputB = 'iso_muons',
)


from heppy.analyzers.ResonanceBuilder import ResonanceBuilder
zeds_muons = cfg.Analyzer(
      ResonanceBuilder,
      output = 'zeds_muons',
      leg_collection = 'iso_muons',
      pdgid = 23
)

zeds_electrons = cfg.Analyzer(
      ResonanceBuilder,
      output = 'zeds_electrons',
      leg_collection = 'iso_electrons',
      pdgid = 23
)

zeds = cfg.Analyzer(
      Merger,
      instance_label = 'merge_zeds',
      inputA = 'zeds_electrons',
      inputB = 'zeds_muons',
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
gen_tree = cfg.Analyzer(
    HTo4lTreeProducer,
    #zeds = 'zeds_electrons',
    zeds = 'zeds',
    higgses = 'higgses',
)


# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence( [
    source,
    iso_photons, 
    muons,
    electrons,
    iso_muons,
    iso_electrons,
    iso_leptons,
    zeds_electrons,
    zeds_muons,
    zeds,
    selection,
    higgses,
    gen_tree,
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
