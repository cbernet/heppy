from framework.analyzer import Analyzer
from particles.physicsobjects import Particle
from utils.deltar import inConeCollection

class LeptonAnalyzer(Analyzer):

    def process(self, event):
        # just a shortcut
        store = event.input
        # access particles, filter out particles with ID as specified in the config file,
        # and store in the event
        particles = map(Particle, store.get("GenParticle"))
        leptons = [ptc for ptc in particles if abs(ptc.ID()) == self.cfg_ana.id ]

        # kinematic selection and ID
        leptons = [lep for lep in leptons if self.kine_sel(lep) and self.id_sel(lep)]

        # isolation
        for lepton in leptons:
            lepton.incone = inConeCollection(lepton, particles, deltaRMax=1.)
            lepton.iso = sum( ptc.pt() for ptc in lepton.incone)
            
        # add to the event, with the name given in the config file
        setattr( event, self.cfg_ana.coll_name, leptons)
        if( not hasattr(event, 'leptons') ):
            event.leptons = []
        # if several LeptonAnalyzers run, event.leptons contains all leptons
        # identified by these analyzers
        event.leptons.extend(leptons) 
        
    def kine_sel(self, particle):
        p4 = particle.P4()
        if( p4.Pt > self.cfg_ana.pt and \
            abs(p4.Eta) < self.cfg_ana.eta ):
            return True
        else:
            return False

    def id_sel(self, lepton):
        if lepton.ID() == 4:
            return self.electron_id_sel(lepton)
        elif lepton.ID() == 5:
            return self.muon_id_sel(muon)

    # the following is temporary:
    # all leptons are considered to be identified for now
        
    # the rhs is a lambda statement defining a 2-parameter function
    # that returns True.
    # this function is bound to this class with the name dummy_id_sel
    dummy_id_sel = lambda x, y: True

    # the function electron_id_sel is in fact dummy_id_sel
    electron_id_sel = dummy_id_sel

    # same for muon id
    muon_id_sel = dummy_id_sel
