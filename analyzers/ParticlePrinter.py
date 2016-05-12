from heppy.framework.analyzer import Analyzer
import shelve

outfilename = 'particles.shv'

class SimpleParticle(object):
    def __init__(self, ptc):
        self.theta = ptc.theta()
        self.phi = ptc.phi()
        self.energy = ptc.e()
        self.pdgid = ptc.pdgid()

    def __str__(self):
        return 'particle: {id} : theta={theta}, phi={phi}, energy={energy}'.format(
            id = self.pdgid,
            theta = self.theta,
            phi = self.phi,
            energy = self.energy
            )
    
class SimpleEvent(object):
    def __init__(self, ievent, ptcs):
        self.ievent = ievent
        self.ptcs = map(SimpleParticle, ptcs)

    def __str__(self):
        lines = ['event {iev}'.format(iev=self.ievent)]
        lines.extend( map(str, self.ptcs) )
        return '\n'.join(lines)
        
        

class ParticlePrinter(Analyzer):

    def beginLoop(self, setup):
        super(ParticlePrinter, self).beginLoop(setup)
        self.events = []

    def process(self, event):
        ptcs = getattr(event, self.cfg_ana.particles )
        self.events.append(SimpleEvent(event.iEv, ptcs)) 
        
    def endLoop(self, setup):
        super(ParticlePrinter, self).endLoop(setup)
        out = shelve.open('/'.join([self.dirName, outfilename]))
        out['events'] = self.events
        out.close()


if __name__ == '__main__':

    sh = shelve.open(outfilename)
    events = sh['events']
    for event in events:
        print event
