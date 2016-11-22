from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *
from heppy.particles.tlv.resonance import Resonance2 as Resonance

from ROOT import TFile

class HTo4lTreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(HTo4lTreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'tree.root']),
                              'recreate')
        self.tree = Tree( 'events', '')
        self.tree.var('weight', float)

        bookParticle(self.tree, 'zed1')
        bookParticle(self.tree, 'zed2')
        bookLepton(self.tree, 'zed1_lep1')
        bookLepton(self.tree, 'zed1_lep2')
        bookLepton(self.tree, 'zed2_lep1')
        bookLepton(self.tree, 'zed2_lep2')
        bookParticle(self.tree, 'higgs')

        bookParticle(self.tree, 'gen_zed1')
        bookParticle(self.tree, 'gen_zed2')
        bookLepton(self.tree, 'gen_zed1_lep1')
        bookLepton(self.tree, 'gen_zed1_lep2')
        bookLepton(self.tree, 'gen_zed2_lep1')
        bookLepton(self.tree, 'gen_zed2_lep2')
        bookParticle(self.tree, 'gen_higgs')


    def process(self, event):
        self.tree.reset()
        zeds = getattr(event, self.cfg_ana.zeds)
        zeds.sort(key=lambda x: abs(x.m()-91.))
        higgses = getattr(event, self.cfg_ana.higgses)

        self.tree.fill('weight' , event.weight )
        
        if len(zeds) > 1:
            
            # Reco zeds
            fillParticle(self.tree, 'zed1', zeds[0])
            fillParticle(self.tree, 'zed2', zeds[1])

            fillLepton(self.tree, 'zed1_lep1', zeds[0].legs[0])
            fillLepton(self.tree, 'zed1_lep2', zeds[0].legs[1])
            fillLepton(self.tree, 'zed2_lep1', zeds[1].legs[0])
            fillLepton(self.tree, 'zed2_lep2', zeds[1].legs[1])

            # MC truth zeds
            gen_zeds = []
            gen_zeds.append(Resonance(zeds[0].legs[0].gen, zeds[0].legs[1].gen, 23))
            gen_zeds.append(Resonance(zeds[1].legs[0].gen, zeds[1].legs[1].gen, 23))

            fillParticle(self.tree, 'gen_zed1', gen_zeds[0])
            fillParticle(self.tree, 'gen_zed2', gen_zeds[1])

            fillLepton(self.tree, 'gen_zed1_lep1', gen_zeds[0].legs[0])
            fillLepton(self.tree, 'gen_zed1_lep2', gen_zeds[0].legs[1])
            fillLepton(self.tree, 'gen_zed2_lep1', gen_zeds[1].legs[0])
            fillLepton(self.tree, 'gen_zed2_lep2', gen_zeds[1].legs[1])

        if len(higgses) > 0:  
            
            # Reco Higgs
            higgs = higgses[0]
            fillParticle(self.tree, 'higgs', higgs)

            # MC truth Higgs
            gen_higgs = Resonance(gen_zeds[0], gen_zeds[1], 25)
            fillParticle(self.tree, 'gen_higgs', gen_higgs)

        self.tree.tree.Fill()
        
    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()

