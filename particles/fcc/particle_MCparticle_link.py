from heppy.particles.object_link import ObjectLink as BaseLink
from pod import POD
from heppy.papas.data.idcoder import IdCoder

from ROOT import TLorentzVector
from ROOT import TVector3

class ParticleMCParticleLink(BaseLink, POD):
    '''Interface for link between fcc particle and MCParticle as stored in a ParticleMCParticle association
    contains the ids of the particle sim and MCparticle rec
    '''
    def __init__(self, fccobj, parenttype='g', childtype='r'):
        super(ObjectLink, self).__init__(fccobj)
        self._id1 =  (fccobj.sim().getObjectID().index,
            fccobj.sim().getObjectID().collectionID)
        self._id2 =  (fccobj.rec().getObjectID().index,
            fccobj.rec().getObjectID().collectionID)
 