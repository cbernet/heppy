from heppy.framework.analyzer import Analyzer
# from heppy.utils.deltar import matchObjectCollection, deltaR

from ROOT import gSystem
gSystem.Load('libDataFormatsParticleFlowReco')

from ROOT import reco 

def get_elements(particle): 
    elements = []
    ele_in_blocks = particle.elementsInBlocks()
    for ele in ele_in_blocks:
        block = ele.first.get()
        index = ele.second
        elements.append(block.elements()[index])
    return elements

def get_tracks(elements):
    tracks = []
    for elem in elements:
        if elem.type() == reco.PFBlockElement.TRACK:
            tracks.append(elem.trackRef().get()) 
    return tracks

class PFAnalyzer(Analyzer):
    
    def process(self, event):
        print 'event', event.iEv
        particles = getattr(event, self.cfg_ana.particles)
        self.study_doublecount_phot(particles)

    
    def study_doublecount_phot(self, particles):
        chadrons = [ptc for ptc in particles if abs(ptc.pdgid())==211]
        if len(chadrons) == 0:
            print 'no charged hadrons'
            return 
        elif len(chadrons) > 1: 
            raise ValueError( '>1 charged hadron! should not happen...' ) 

        print '-'*50
        chadron = chadrons[0]
        chadron_elements = get_elements(chadron)
        print chadron 
        for elem in chadron_elements: 
            print '\t', elem
        tracks = get_tracks(chadron_elements)
        assert(len(tracks)==1)
        track = tracks[0]
        print '\tchadron', chadron.pt()
        print '\ttrack', track.pt()
        if hasattr(chadron, 'match_211'):
            genchadron = chadron.match_211
            print '\tgen  ', genchadron.pt()
        else: 
            print '\tno gen charged hadron!', chadron.match

