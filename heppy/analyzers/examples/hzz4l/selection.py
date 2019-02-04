from heppy.framework.analyzer import Analyzer
from heppy.statistics.counter import Counter

class Selection(Analyzer):

    def beginLoop(self, setup):
        super(Selection, self).beginLoop(setup)
        self.counters.addCounter('cut_flow') 
        self.counters['cut_flow'].register('All events')
        self.counters['cut_flow'].register('At least one Z -> l+ l- candidates')
        self.counters['cut_flow'].register('40 < mZ1 < 120')
        self.counters['cut_flow'].register('At least a second Z -> l+ l- candidates')
	self.counters['cut_flow'].register('12 < mZ2 < 120')
        self.counters['cut_flow'].register('leading lepton pT > 20')
        self.counters['cut_flow'].register('sub-leading lepton pT > 10')

    def process(self, event):
        self.counters['cut_flow'].inc('All events')

        zeds = event.zeds

        #select events with at least one Z -> l+ l- candidates
        if (len(zeds) < 1):
           return False
        self.counters['cut_flow'].inc('At least one Z -> l+ l- candidates')

        # select events with 40 < m_Z1 < 120 
        if (zeds[0].m() < 40. or zeds[0].m() > 120. ) :
            return False
        self.counters['cut_flow'].inc('40 < mZ1 < 120')

        #select events with at least a second Z -> l+ l- candidates
        if (len(zeds) < 2):
           return False
        self.counters['cut_flow'].inc('At least a second Z -> l+ l- candidates')

        # select events with 12 < m_Z2 < 120 
        if (zeds[1].m() < 12. or zeds[1].m() > 120. ):
            return False
        self.counters['cut_flow'].inc('12 < mZ2 < 120')

        leptons = []
        for i in range(2):
           leptons.append(zeds[i].leg1())
           leptons.append(zeds[i].leg2())

        leptons.sort(key=lambda x: x.pt(), reverse=True)
        
        # select event with leading lepton pT > 20
        if (leptons[0].pt() < 20.):
            return False
        self.counters['cut_flow'].inc('leading lepton pT > 20')

        # select event with subleading lepton pT > 10
        if (leptons[1].pt() < 10.):
            return False
        self.counters['cut_flow'].inc('sub-leading lepton pT > 10')
        
        return True
