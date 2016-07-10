from heppy.particles.particle import Particle as BaseParticle
from vertex import Vertex
from pod import POD
from ROOT import TLorentzVector
from heppy.papas.data.identifier import Identifier
from heppy.papas.cpp.physicsoutput import PhysicsOutput as pdebug
import copy

class Particle(BaseParticle, POD):
    
    def __init__(self, fccobj):
        super(Particle, self).__init__(fccobj)
        self.uniqueid=Identifier.make_id(Identifier.PFOBJECTTYPE.PARTICLE)
        self._charge = fccobj.Core().Charge
        self._pid = fccobj.Core().Type
        self._status = fccobj.Core().Status
        if hasattr(fccobj, 'StartVertex'):
            start = fccobj.StartVertex()
            self._start_vertex = Vertex(start) if start.isAvailable() \
                                 else None 
            end = fccobj.EndVertex()
            self._end_vertex = Vertex(end) if end.isAvailable() \
                               else None 
        self._tlv = TLorentzVector()
        p4 = fccobj.Core().P4
        self._tlv.SetXYZM(p4.Px, p4.Py, p4.Pz, p4.Mass)
        #write(str('Made Pythia {}').format(self))
        
    def __deepcopy__(self, memodict={}):
        newone = type(self).__new__(type(self))
        for attr, val in self.__dict__.iteritems():
            if attr not in ['fccobj', '_start_vertex', '_end_vertex']:
                setattr(newone, attr, copy.deepcopy(val, memodict))
        return newone

    
    def __str__(self):
        tmp = '{className} :{uniqueid:9}:{uid}: pdgid = {pdgid:5}, status = {status:3}, q = {q:2}, {p4}'
        p4='pt = {pt:5.1f}, e = {e:5.1f}, eta = {eta:5.2f}, theta = {theta:5.2f}, phi = {phi:5.2f}, mass = {m:5.2f}'.format(
            pt = self.pt(),
            e = self.e(),
            eta = self.eta(),
            theta = self.theta(),
            phi = self.phi(),
            m = self.m()  ) 
        
        pid=self.pdgid()
        if self.q() == 0 and self.pdgid() < 0:
            pid = -self.pdgid();   
        return tmp.format(
            className = self.__class__.__name__,
            uniqueid = Identifier.pretty(self.uniqueid),
            uid=self.uniqueid,
            pdgid = pid,
            status = self.status(),
            q = self.q(),
            p4 = p4
                    
        )