from detector import Detector, DetectorElement
import material
from geometry import VolumeCylinder
import math
import random

class ECAL(DetectorElement):

    def __init__(self):
        volume = VolumeCylinder('ecal', 1.55, 2.1, 1.30, 2. )
        mat = material.Material('ECAL', 8.9e-3, 0.275)
        self.eta_crack = 1.5
        self.emin = 0.4
        self.eres = [0.073, 0.1, 0.005]
        super(ECAL, self).__init__('ecal', volume,  mat)
        
    def energy_resolution(self, energy, theta=0.):
        stoch = self.eres[0] / math.sqrt(energy)
        noise = self.eres[1] / energy
        constant = self.eres[2]
        return math.sqrt( stoch**2 + noise**2 + constant**2) 

    def cluster_size(self, ptc):
        pdgid = abs(ptc.pdgid())
        if pdgid==22 or pdgid==11:
            return 0.04
        else:
            return 0.07

    def acceptance(self, cluster):
        energy = cluster.energy
        eta = abs(cluster.position.Eta())
        if eta < self.eta_crack:
            return energy>self.emin
        elif eta < 3.:
            return energy>self.emin and cluster.pt>0.5
        else:
            return False

    def space_resolution(self, ptc):
        pass

    
class HCAL(DetectorElement):

    def __init__(self):
        volume = VolumeCylinder('hcal', 2.9, 3.6, 1.9, 2.6 )
        mat = material.Material('HCAL', None, 0.17)
        self.eres = [1.1, 0., 0.]
        super(HCAL, self).__init__('ecal', volume, mat)

    def energy_resolution(self, energy, theta=0.):
        return self.eres[0]/ math.sqrt( energy ) 

    def cluster_size(self, ptc):
        return 0.2

    def acceptance(self, cluster):
        energy = cluster.energy
        eta = abs(cluster.position.Eta())
        if eta < 3. : 
            return energy>4.
        elif eta < 5.:
            return energy>7.
        else:
            return False
    
    def space_resolution(self, ptc):
        pass


    
class Tracker(DetectorElement):
    #TODO acceptance and resolution depend on the particle type
    
    def __init__(self):
        volume = VolumeCylinder('tracker', 1.29, 1.99)
        mat = material.void
        super(Tracker, self).__init__('tracker', volume,  mat)

    def acceptance(self, track):
        # return False
        pt = track.pt
        eta = abs(track.p3.Eta())
        if eta < 2.5 and pt>0.5:
            return random.uniform(0,1)<1. # CMS without tracker material effects 
        else:
            return False

    def pt_resolution(self, track):
        # TODO: depends on the field
        pt = track.pt
        return 5e-3

    

class Field(DetectorElement):

    def __init__(self, magnitude):
        self.magnitude = magnitude
        volume = VolumeCylinder('field', 2.9, 3.6)
        mat = material.void
        super(Field, self).__init__('tracker', volume,  mat)
        
        
class CMS(Detector):
    
    def __init__(self):
        super(CMS, self).__init__()
        self.elements['tracker'] = Tracker()
        self.elements['ecal'] = ECAL()
        self.elements['hcal'] = HCAL()
        self.elements['field'] = Field(3.8)

cms = CMS()
