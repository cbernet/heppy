from heppy.particles.particle import Particle as BaseParticle
from vertex import Vertex
from pod import POD
from ROOT import TLorentzVector
from heppy.papas.data.identifier import Identifier
from heppy.utils.pdebug import pdebugger
import copy

class Particle(BaseParticle, POD):
    
    def __init__(self, fccobj):
        super(Particle, self).__init__(fccobj)
        self.uniqueid=Identifier.make_id(Identifier.PFOBJECTTYPE.PARTICLE)
        self._charge = fccobj.core().charge
        self._pid = fccobj.core().pdgId
        self._status = fccobj.core().status
        if hasattr(fccobj, 'startVertex'):
            start = fccobj.startVertex()
            self._start_vertex = Vertex(start) if start.isAvailable() \
                                 else None 
            end = fccobj.endVertex()
            self._end_vertex = Vertex(end) if end.isAvailable() \
                               else None 
        self._tlv = TLorentzVector()
        p4 = fccobj.core().p4
        self._tlv.SetXYZM(p4.px, p4.py, p4.pz, p4.mass)
        #write(str('Made Pythia {}').format(self))
        
    def __deepcopy__(self, memodict={}):
        newone = type(self).__new__(type(self))
        for attr, val in self.__dict__.iteritems():
            if attr not in ['fccobj', '_start_vertex', '_end_vertex']:
                setattr(newone, attr, copy.deepcopy(val, memodict))
        return newone

    def __str__(self):
        mainstr =  super(Particle, self).__str__()
        idstr = '{pretty:6}:{id}'.format(
            pretty = Identifier.pretty(self.uniqueid),
            id = self.uniqueid)
        fields = mainstr.split(':')
        fields.insert(1, idstr)
        return ':'.join(fields)     

