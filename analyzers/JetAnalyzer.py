from framework.analyzer import Analyzer
from particles.physicsobjects import Jet, Particle

class JetAnalyzer(Analyzer):

    def process(self, event):
        # just a shortcut
        store = event.input
        # the constructor of the Jet class is invoked on each POD in the GenJet collection
        # the result is a list of Jets, stored in the python event
        event.jets = map(Jet, store.get("GenJet"))
        # looking for associated particles
        jetparticles = store.get("GenJetParticle")
        particles = map(Particle, store.get("GenParticle"))
        # copying the list of particles (the objects in the list are NOT copied)
        event.unclustered_particles = list(particles) 
        for jet in event.jets:
            jet.particles = [] # attaching empty list of particles to the jet object
            for assoc in jetparticles:
                if jet == assoc.Jet():
                    jet.particles.append( assoc.Particle() )
                    event.unclustered_particles.remove( assoc.Particle() )
            if (self.cfg_ana.verbose):
                print 'jet',jet.P4().Pt, jet.P4().Eta
                for ptc in jet.particles:
                    print '\tparticle', ptc.ID(), ptc.P4().Pt, ptc.P4().Eta
        if(self.cfg_ana.verbose):
            print 'number of unclustered particles:',len(event.unclustered_particles)
        # sorting jets by pt.
        # first create a collection of tuples (jet, jet_pt)
        indexedjets = zip(event.jets, [jet.P4().Pt for jet in event.jets])
        # sorting this collection according to the second field in the tuple
        indexedjets.sort(key = lambda x: x[1], reverse=True)
        # unzipping. The two lines below are equivalent,
        # and the second probably more readable
        # event.jets = list( zip(*indexedjets)[0] )
        event.jets = [ jet for jet, pt in indexedjets]
