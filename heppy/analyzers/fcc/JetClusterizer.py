'''Jet clusterizer based on fastjet.'''

from heppy.framework.analyzer import Analyzer

from heppy.particles.tlv.jet import Jet
from heppy.particles.jet import JetConstituents

import os 

from ROOT import gSystem
CCJetClusterizer = None
if os.environ.get('FCCPHYSICS'):
    gSystem.Load("libfccphysics-tools")
    from ROOT import JetClusterizer as CCJetClusterizer
elif os.environ.get('CMSSW_BASE'):
    gSystem.Load("libColinPFSim")
    from ROOT import heppy
    CCJetClusterizer = heppy.JetClusterizer


class JetClusterizer(Analyzer):
    '''Jet clusterizer based on fastjet (kt-ee algorithm)
    
    This analyzer, specific to the FCC,
    makes use of the JetClusterizer class compiled in the fcc-physics package.

    Example configuration::

        from heppy.analyzers.fcc.JetClusterizer import JetClusterizer
        jets = cfg.Analyzer(
          JetClusterizer,
          output = 'jets',
          particles = 'particles_not_zed',
          fastjet_args = dict(njets = 2)  
        )
    
    @param output: name of the output collection of L{jets<heppy.particles.jet.Jet>}. 
      Each jet is attached a L{JetConstituents<heppy.particles.jet.JetConstituents>} object
      as C{jet.constituents}.

    @param particles: name of the input collection of particle-like objects. 
      These objects should have a p4(). 
    
    @param fastjet_args: fastjet arguments. 
      you should provide either one or the other of the following arguments:
       - ptmin : pt threshold in GeV for exclusive jet reconstruction 
       - njets : number of jets for inclusive jet reconstruction 
       
    '''

    def __init__(self, *args, **kwargs):
        super(JetClusterizer, self).__init__(*args, **kwargs)
        args = self.cfg_ana.fastjet_args
        self.clusterize = None
        self.njets = 0
        if 'ptmin' in args and 'njets' in args:
            raise ValueError('cannot specify both ptmin and njets arguments')
        if 'ptmin' in args:
            self.clusterizer = CCJetClusterizer(0)
            def clusterize():
                return self.clusterizer.make_inclusive_jets(args['ptmin']) 
            self.clusterize = clusterize
        elif 'njets' in args:
            self.njets = args['njets']
            self.clusterizer = CCJetClusterizer(1)
            def clusterize():
                return self.clusterizer.make_exclusive_jets(self.njets) 
            self.clusterize = clusterize
        else:
            raise ValueError('specify either ptmin or njets') 
        
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
        '''Process event.
        
        The event must contain:
         - self.cfg_ana.particles: the list of particles to be clustered
         
        This method creates:
         - event.<self.cfg_ana.output>: the list of L{jets<heppy.particles.jet.Jet>}. 
        '''
        particles = getattr(event, self.cfg_ana.particles)
        # removing neutrinos
        particles = [ptc for ptc in particles if abs(ptc.pdgid()) not in [12,14,16]]
        if len(particles) < self.njets:
            if hasattr(self.cfg_ana, 'njets_required') and self.cfg_ana.njets_required == False:
                # not enough particles for the required number of jets,
                # making no jet
                setattr(event, self.cfg_ana.output, [])
                return True                

            else:
                # njets_required not provided, or njets_required set to True
                err = 'Cannot make {} jets with {} particles -> Event discarded'.format(
                    self.njets, len(particles)
                )
                self.mainLogger.error(err)
                # killing the sequence, as the user requests exactly njets
                return False
        # enough particles to make the required number of jets
        self.clusterizer.clear()
        for ptc in particles:
            self.clusterizer.add_p4( ptc.p4() )
        self.clusterize()
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
        setattr(event, self.cfg_ana.output, jets)
