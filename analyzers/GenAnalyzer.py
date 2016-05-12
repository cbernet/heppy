from heppy.framework.analyzer import Analyzer
from heppy.particles.genbrowser import GenBrowser

class GenAnalyzer(Analyzer):
    
    def process(self, event):
        genptcs = event.gen_particles
        event.bquarks = [ptc for ptc in genptcs if abs(ptc.pdgid())==5 and
                         ptc.status()==23]
        if len(event.bquarks)==2:
            print map(str, event.bquarks)
            event.genbrowser = GenBrowser(event.gen_particles,
                                          event.gen_vertices)
            for bquark in event.bquarks:
                print bquark
                descendents = event.genbrowser.descendants(bquark)
                for dsc in descendents:
                    if dsc.status()==1 and dsc.q():
                        print '\t', dsc
                        print '\t\t', dsc.start_vertex()
