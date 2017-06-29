'''CLIC-ILD model'''

from detector import Detector, DetectorElement
import material as material
from geometry import VolumeCylinder
import math
import heppy.statistics.rrandom as random

class ECAL(DetectorElement):

    def __init__(self):
        depth = 0.25
        inner_radius = 2.15
        inner_z = 2.6
        nX0 = 23  #CLIC CDR, page 70, value for CLIC_ILD
        nLambdaI = 1  # ibid
        outer_radius = inner_radius + depth
        outer_z = inner_z + depth
        X0 = depth / nX0
        lambdaI = depth / nLambdaI
        volume = VolumeCylinder('ecal', outer_radius, outer_z, inner_radius, inner_z)
        mat = material.Material('ECAL', X0, lambdaI)
        # todo: recompute
        self.eta_junction = volume.inner.eta_junction()
        # as for ILD (thresholds chosen by Mogens)
        self.emin = {'barrel':0.5, 'endcap':0.5}
        # CLIC CDR p.123. adding a noise term of 1%
        self.eres = {'barrel':[0.165, 0.010, 0.015]}
        super(ECAL, self).__init__('ecal', volume,  mat)

    def energy_resolution(self, energy, eta=0.):
        part = 'barrel'
        stoch = self.eres[part][0] / math.sqrt(energy)
        noise = self.eres[part][1] / energy
        constant = self.eres[part][2]
        return math.sqrt( stoch**2 + noise**2 + constant**2) 

    def energy_response(self, energy, eta=0):
        return 1
    
    def cluster_size(self, ptc):
        '''just guessing numbers (from Mogens, as in ILD).'''
        pdgid = abs(ptc.pdgid())
        if pdgid==22 or pdgid==11:
            return 0.015
        else:
            return 0.045

    def acceptance(self, cluster):
        energy = cluster.energy
        eta = abs(cluster.position.Eta())
        if eta < self.eta_junction:
            return energy>self.emin['barrel']
        elif eta < 2.76:  #TODO check this value
            return energy>self.emin['endcap']
        else:
            return False

    def space_resolution(self, ptc):
        pass
    
    
class HCAL(DetectorElement):

    def __init__(self):
        volume = VolumeCylinder('hcal', 4.8, 5.3, 2.4, 2.85 )
        # not sure about X0 and lambda_i, but these don't matter anyway
        mat = material.Material('HCAL', 0.018, 0.17)
        # resolution from CLIC CDR Fig. 6.11, 1st hypothesis
        self.eres = [0.60, 0., 0.025]        
        super(HCAL, self).__init__('ecal', volume, mat)

    def energy_resolution(self, energy, eta=0.):
        stoch = self.eres[0] / math.sqrt(energy)
        noise = self.eres[1] / energy
        constant = self.eres[2]
        return math.sqrt( stoch**2 + noise**2 + constant**2)

    def energy_response(self, energy, eta=0):
        return 1.0
    
    def cluster_size(self, ptc):
        '''returns cluster size in the HCAL
        
        25 cm for CLIC, c.f. CLIC CDR Fig. 6.12
        Value taken to get a 80% chance of separating two showers.
        '''
        return 0.25

    def acceptance(self, cluster):
        energy = cluster.energy
        eta = abs(cluster.position.Eta())
        if eta < 2.76:  #TODO: check this value
            return energy>1.
        else:
            return False
    
    def space_resolution(self, ptc):
        pass


    
class Tracker(DetectorElement):
    #TODO acceptance and resolution 
    #depend on the particle type
    
    def __init__(self):
        volume = VolumeCylinder('tracker', 2.14, 2.6)
        mat = material.void
        super(Tracker, self).__init__('tracker', volume,  mat)

    def acceptance(self, track):
        # return False
        pt = track.p3() .Pt()
        eta = abs(track.p3() .Eta())
        if eta < 3. and pt > 0.5:  #TODO check these values 
            return True
        else:
            return False

    def resolution(self, track):
        # TODO: depends on the field
        pt = track.p3() .Pt()
        return 1.1e-2

    

class Field(DetectorElement):

    def __init__(self, magnitude):
        self.magnitude = magnitude
        volume = VolumeCylinder('field', 4.8, 5.3)
        mat = material.void
        super(Field, self).__init__('tracker', volume,  mat)

class BeamPipe(DetectorElement):
    '''Beam pipe is not used in the simulation at the moment, so no need to define it.'''

    def __init__(self):
        #Material Seamless AISI 316 LN, External diameter 53 mm, Wall thickness 1.5 mm (hors CLIC) X0 1.72 cm
        #in CLIC, radius 25 mm (?), tchikness 8mm, X0 35.28 cm : berylluim
        factor = 1.0
        volume = VolumeCylinder('beampipe', 2.5e-2*factor+0.8e-3, 1.98, 2.5e-2*factor, 1.9785 )
        mat = material.Material('BeamPipe', 35.28e-2, 0)
        super(BeamPipe, self).__init__('beampipe', volume, mat)

        
class CLIC(Detector):
        
    def electron_acceptance(self, track):
        return track.p3() .Mag() > 5 and abs(track.p3() .Eta()) < 2.5

    def electron_resolution(self, ptc):
        return 0.1 / math.sqrt(ptc.e())
            
    def muon_acceptance(self, track):
        return track.p3() .Pt() > 5 and abs(track.p3() .Eta()) < 2.5
            
    def muon_resolution(self, ptc):
        return 0.02 
    
    def __init__(self):
        super(CLIC, self).__init__()
        self.elements['tracker'] = Tracker()
        self.elements['ecal'] = ECAL()
        self.elements['hcal'] = HCAL()
        # field limited to 2T for FCC-ee
        self.elements['field'] = Field(2.)
        self.elements['beampipe'] = BeamPipe()

clic = CLIC()
