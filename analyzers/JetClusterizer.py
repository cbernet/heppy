from heppy.framework.analyzer import Analyzer
from heppy.framework.event import Event
from heppy.particles.tlv.jet import Jet
from heppy.particles.jet import JetConstituents

import os 

from ROOT import gSystem
CCJetClusterizer = None
if os.environ.get('ANALYSISCPP'):
    gSystem.Load("libanalysiscpp-tools")
    from ROOT import JetClusterizer as CCJetClusterizer
elif os.environ.get('CMSSW_BASE'):
    gSystem.Load("libColinPFSim")
    from ROOT import heppy
    CCJetClusterizer = heppy.JetClusterizer

import math
    
class JetClusterizer(Analyzer):
    '''Jet clusterizer. 
    
    Makes use of the JetClusterizer class compiled in the analysis-cpp package. 

    Example configuration: 

    papas_jets = cfg.Analyzer(
       JetClusterizer,
       instance_label = 'papas', 
       particles = 'papas_rec_particles'
    )

    particles: Name of the input particle collection.
    The output jet collection name is built from the instance_label, 
    in this case "papas_jets".
    '''

    def __init__(self, *args, **kwargs):
        super(JetClusterizer, self).__init__(*args, **kwargs)
        min_e = 0.
        self.clusterizer = CCJetClusterizer(min_e)

    def validate(self, jet):
        constits = jet.constituents
        keys = set(jet.constituents.keys())
        all_possible = set([211, 22, 130, 11, 13, 1, 2])
        if not keys.issubset(all_possible):
            print constits
            assert(False)
        sume = 0. 
        for component in jet.constituents.values():
            if component.e() - jet.e() > 1e-5:
                import pdb; pdb.set_trace()
            sume += component.e()
        if jet.e() - sume > 1e-5:
            import pdb; pdb.set_trace()
                
                
    def process(self, event):
        particles = getattr(event, self.cfg_ana.particles)
        # removing neutrinos
        particles = [ptc for ptc in particles if abs(ptc.pdgid()) not in [12,14,16]]
        self.clusterizer.clear();
        for ptc in particles:
            self.clusterizer.add_p4( ptc.p4() )
        self.clusterizer.clusterize()
        jets = []
        for jeti in range(self.clusterizer.n_jets()):
            jet = Jet( self.clusterizer.jet(jeti) )
            jet.constituents = JetConstituents()
            jets.append( jet )
            for consti in range(self.clusterizer.n_constituents(jeti)):
                constituent_index = self.clusterizer.constituent_index(jeti, consti)
                constituent = particles[constituent_index]
                jet.constituents.append(constituent)
            jet.constituents.sort()
            self.validate(jet)
        setattr(event, self.instance_label, jets)
