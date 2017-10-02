from heppy.particles.object_link import ObjectLink as BaseLink
from pod import POD
from heppy.papas.data.identifier import Identifier

from ROOT import TLorentzVector
from ROOT import TVector3

class ObjectLink(BaseLink, POD):

    def __init__(self, fccobj, parenttype='g', childtype='r'):
        super(ObjectLink, self).__init__(fccobj)
        self.incoming = []
        self.outgoing = []
        tlv = TLorentzVector()
        #papas id for sim particle
        p4 = fccobj.sim().core().p4
        tlv.SetXYZM(p4.px, p4.py, p4.pz, p4.mass)
        #self._id1= Identifier.make_id(Identifier.PFOBJECTTYPE.PARTICLE, fccobj.sim().getObjectID().index, parenttype, tlv.E())
        self._id1 = fccobj.sim().getObjectID()
        #papas id for rec particle
        p4 = fccobj.rec().core().p4
        tlv.SetXYZM(p4.px, p4.py, p4.pz, p4.mass)
        #self._id2= Identifier.make_id(Identifier.PFOBJECTTYPE.PARTICLE, fccobj.rec().getObjectID().index, childtype, tlv.E())
        self._id2 = fccobj.rec().getObjectID()
