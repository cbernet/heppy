'''Select stable generated charged hadrons from b-quark decay'''


from heppy.framework.analyzer import Analyzer
from heppy.particles.genbrowser import GenBrowser
from heppy.particles.pdgcodes import hasBottom

class ChargedHadronsFromB(Analyzer):
    '''Select stable generated charged hadrons from b-quark decay'''

    def process(self, event):
        '''event should contain:
        
        * gen_particles: list of all stable gen particles
        '''
        genptcs = event.gen_particles
        bquarks = []
        charged_hadrons = []
        event.hadrons_from_b = []
        for ptc in genptcs:
            if abs(ptc.pdgid())==5:
                bquarks.append(ptc)
            elif ptc.q() and ptc.status()==1:
                charged_hadrons.append(ptc)
        if len(bquarks) == 0 or len(charged_hadrons) == 0:
            return
        event.genbrowser = GenBrowser(event.gen_particles,
                                      event.gen_vertices)
        event.hadrons_from_b = []
        event.hadrons_not_from_b = []
        for hadron in charged_hadrons:
            is_from_b = is_ptc_from_b(event, hadron, event.genbrowser)
            if is_from_b:
                event.hadrons_from_b.append(hadron)
            else:
                event.hadrons_not_from_b.append(hadron)

def is_ptc_from_b(event, hadron, browser):
    ancestors = browser.ancestors(hadron)
    is_from_b = False 
    for ancestor in ancestors:
        if hasBottom(ancestor.pdgid() ):
            is_from_b = True
    return is_from_b
            
        
