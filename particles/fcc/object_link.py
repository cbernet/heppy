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
        self._id1 =  (fccobj.sim().getObjectID().index,
                       fccobj.sim().getObjectID().collectionID) 
        self._id2 =  (fccobj.rec().getObjectID().index,
                      fccobj.rec().getObjectID().collectionID)         
 