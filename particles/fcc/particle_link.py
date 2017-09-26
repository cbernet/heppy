from heppy.particles.particle_link import Particle_Link as BaseLink
from pod import POD
from heppy.papas.data.identifier import Identifier

from ROOT import TLorentzVector
from ROOT import TVector3

class Particle_Link(BaseLink, POD):

    def __init__(self, fccobj, parenttype='g', childtype='r'):
        super(Particle_Link, self).__init__(fccobj)
        self.incoming = []
        self.outgoing = []
        tlv = TLorentzVector()
        #papas id for sim particle
        #self._parent= fccobj.sim().getObjectID().index
        #self._child= fccobj.rec().getObjectID().index
        p4 = fccobj.sim().core().p4
        tlv.SetXYZM(p4.px, p4.py, p4.pz, p4.mass)
        self._parentid= Identifier.make_id(Identifier.PFOBJECTTYPE.PARTICLE, fccobj.sim().getObjectID().index, parenttype, tlv.E())
        #papas id for rec particle
        p4 = fccobj.rec().core().p4
        tlv.SetXYZM(p4.px, p4.py, p4.pz, p4.mass)
        self._childid= Identifier.make_id(Identifier.PFOBJECTTYPE.PARTICLE, fccobj.rec().getObjectID().index, childtype, tlv.E())
  

