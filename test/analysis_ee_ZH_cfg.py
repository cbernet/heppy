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
    files = ['example.root']
)
selectedComponents = [comp]

from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    mode = 'ee',
    gen_particles = 'GenParticle',
)  

# currently treating electrons and muons transparently.
# could use the same modules to have a collection of electrons
# and a collection of muons 
from heppy.analyzers.Filter import Filter
leptons = cfg.Analyzer(
    Filter,
    'sel_leptons',
    output = 'leptons',
    input_objects = 'gen_particles_stable',
    filter_func = lambda ptc: ptc.e()>10. and abs(ptc.pdgid()) in [11, 13]
)

from heppy.analyzers.LeptonAnalyzer import LeptonAnalyzer
from heppy.particles.isolation import EtaPhiCircle
iso_leptons = cfg.Analyzer(
    LeptonAnalyzer,
    leptons = 'leptons',
    particles = 'gen_particles_stable',
    iso_area = EtaPhiCircle(0.4)
)

#TODO: Colin: would be better to have a lepton class
def relative_isolation(lepton):
    sumpt = lepton.iso_211.sumpt + lepton.iso_22.sumpt + lepton.iso_130.sumpt
    sumpt /= lepton.pt()
    return sumpt

sel_iso_leptons = cfg.Analyzer(
    Filter,
    'sel_iso_leptons',
    output = 'sel_iso_leptons',
    input_objects = 'leptons',
    filter_func = lambda lep : relative_isolation(lep)<0.3 # fairly loose
)

# building Zs's
from heppy.analyzers.ResonanceBuilder import ResonanceBuilder
zeds = cfg.Analyzer(
    ResonanceBuilder,
    output = 'zeds',
    leg_collection = 'sel_iso_leptons',
    pdgid = 23
)

from heppy.analyzers.fcc.Recoil import RecoilBuilder
recoil = cfg.Analyzer(
    RecoilBuilder,
    output = 'recoil',
    sqrts = 240.,
    to_remove = 'zeds_legs'
) 

from heppy.analyzers.Masker import Masker
particles_not_zed = cfg.Analyzer(
    Masker,
    output = 'particles_not_zed',
    input = 'gen_particles_stable',
    mask = 'zeds_legs',

)

from heppy.analyzers.fcc.JetClusterizer import JetClusterizer
jets = cfg.Analyzer(
    JetClusterizer,
    instance_label = 'jets',
    particles = 'particles_not_zed',
    fastjet_args = dict( njets = 2)  
)


# TODO redefine tree 
from heppy.analyzers.examples.zh.ZHTreeProducer import ZHTreeProducer
tree = cfg.Analyzer(
    ZHTreeProducer,
    jets = 'jets',
    leptons = 'leptons',
    recoil  = 'recoil'
)

# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence( [
    source,
    leptons,
    iso_leptons,
    sel_iso_leptons,
    zeds,
    recoil,
    particles_not_zed,
    jets,
    tree
    ] )

# comp.files.append('example_2.root')
# comp.splitFactor = 2  # splitting the component in 2 chunks
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

    def next():
        loop.process(loop.iEvent+1)

    loop = Looper( 'looper', config,
                   nEvents=100,
                   nPrint=0,
                   timeReport=True)
    loop.process(6)
    print loop.event
