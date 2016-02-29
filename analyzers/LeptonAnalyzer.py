from heppy.framework.analyzer import Analyzer
from heppy.utils.deltar import matchObjectCollection, deltaR
from heppy.particles.isolation import IsolationComputer, IsolationInfo


pdgids = [211, 22, 130]

class LeptonAnalyzer(Analyzer):

    def beginLoop(self, setup):
        super(LeptonAnalyzer, self).beginLoop(setup)
        # now using same isolation definition for all pdgids
        self.iso_computers = dict()
        for pdgid in pdgids:
            self.iso_computers[pdgid] = IsolationComputer(
                [self.cfg_ana.iso_area],
                label='iso{pdgid}'.format(pdgid=str(pdgid))
            )
            
    def process(self, event):
        particles = getattr(event, self.cfg_ana.particles)
        leptons = getattr(event, self.cfg_ana.leptons)
        for lepton in leptons:
            isosum = IsolationInfo('all', lepton)
            for pdgid in pdgids:
                sel_ptcs = [ptc for ptc in particles if ptc.pdgid()==pdgid]
                iso = self.iso_computers[pdgid].compute(lepton, sel_ptcs)
                isosum += iso 
                setattr(lepton, 'iso_{pdgid}'.format(pdgid=pdgid), iso)
            lepton.iso = isosum
        
  
