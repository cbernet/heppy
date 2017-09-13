from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *

from ROOT import TFile

class ZHTreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(ZHTreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'tree.root']),
                              'recreate')
        self.tree = Tree( 'events', '')
        if hasattr(self.cfg_ana, 'recoil'):
            bookParticle(self.tree, 'recoil')
        if hasattr(self.cfg_ana, 'zeds'):  
            bookZed(self.tree, 'zed')
        self.taggers = ['b', 'bmatch', 'bfrac']
        bookJet(self.tree, 'jet1', self.taggers)
        bookJet(self.tree, 'jet2', self.taggers)
        bookHbb(self.tree, 'higgs')
        bookParticle(self.tree, 'misenergy')
        var(self.tree, 'n_nu')
       
    def process(self, event):
        self.tree.reset()
        if hasattr(self.cfg_ana, 'recoil'):
            recoil = getattr(event, self.cfg_ana.recoil)    
            fillParticle(self.tree, 'recoil', recoil)
        if hasattr(self.cfg_ana, 'zeds'):  
            zeds = getattr(event, self.cfg_ana.zeds)
            if len(zeds)>0:
                zed = zeds[0]
                fillZed(self.tree, 'zed', zed)
        misenergy = getattr(event, self.cfg_ana.misenergy)
        fillParticle(self.tree, 'misenergy', misenergy )        
        jets = getattr(event, self.cfg_ana.jets)
        for ijet, jet in enumerate(jets):
            if ijet == 2:
                break
            fillJet(self.tree, 'jet{ijet}'.format(ijet=ijet+1), jet, self.taggers)
        higgses = getattr(event, self.cfg_ana.higgses)
        if len(higgses)>0:
            higgs = higgses[0]
            # if higgs.m() < 30:
            #    import pdb; pdb.set_trace()
            fillHbb(self.tree, 'higgs', higgs)
        neutrinos = getattr(event, 'neutrinos', None)
        if neutrinos:
            fill(self.tree, 'n_nu', len(neutrinos))
        self.tree.tree.Fill()
        
    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()
        
