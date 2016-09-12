from heppy.particles.particle import Particle as BaseParticle
from rootobj import RootObj
from ROOT import TVector3
from vertex import Vertex 
from heppy.papas.data.identifier import Identifier

import math

class Particle(BaseParticle, RootObj):
    def __init__(self, pdgid, charge, tlv, status=1):
        super(Particle, self).__init__()
        #self.uniqueid=Identifier.make_id(Identifier.PFOBJECTTYPE.PARTICLE)
        self._pid = pdgid
        self._charge = charge
        self._tlv = tlv
        self._status = status
        self._start_vertex = Vertex(TVector3(),0)
        self._end_vertex = None

    #def shortinfo(self):
        #tmp = '{pdgid:} ({e:.1f})'
        ##needed for now to get match with C++
        #pid=self.pdgid()      
        #if self.q() == 0 and pid < 0:
            #pid = -pid        
    
        #return tmp.format(
            #pdgid =pid,
            #e = self.e()        
        #)    

    #def __str__(self):
        #tmp = '{className} :{uniqueid:9}:{uid}: pdgid = {pdgid:5}, status = {status:3}, q = {q:2}, {p4}'
        #p4='pt = {pt:5.1f}, e = {e:5.1f}, eta = {eta:5.2f}, theta = {theta:5.2f}, phi = {phi:5.2f}, mass = {m:5.2f}'.format(
            #pt = self.pt(),
            #e = self.e(),
            #eta = self.eta(),
            #theta = self.theta(),
            #phi = self.phi(),
            #m = self.m()  ) 

        #pid=self.pdgid()
        #if self.q() == 0 and self.pdgid() < 0:
            #pid = -self.pdgid();   
        #return tmp.format(
            #className = self.__class__.__name__,
            #uniqueid = Identifier.pretty(self.uniqueid),
            #uid=self.uniqueid,
            #pdgid = pid,
            #status = self.status(),
            #q = self.q(),
            #p4 = p4

        #)