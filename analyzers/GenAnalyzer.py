from heppy.framework.analyzer import Analyzer
from heppy.particles.genbrowser import GenBrowser

class UserWarning(Exception):
    pass

class GenAnalyzer(Analyzer):
    
    def process(self, event):
        genptcs = event.gen_particles
        event.electrons = [ptc for ptc in genptcs if abs(ptc.pdgid())==11
                           and ptc.status()==1]
        if len(event.electrons)==2:
            print map(str, event.electrons)
            event.genbrowser = GenBrowser(event.gen_particles,
                                          event.gen_vertices)
            for e in event.electrons:
                print e
                ancestors = event.genbrowser.ancestors(e)
                for a in ancestors:
                    if a.status()==22:
                        print '\t', a
            import pdb; pdb.set_trace()
