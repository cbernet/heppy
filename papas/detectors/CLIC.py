'''CLIC-ILD model

TODO : use new tracker momentum resolution (important for muons)
TODO : electron resolution : use quad sum of tracker and ecal resolution
'''

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
        self.eres = {'barrel':[0.167, 0.010, 0.011]}
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
   
    def __init__(self):
        super(Tracker, self).__init__('tracker',
                                      VolumeCylinder('tracker', 2.14, 2.6),
                                      material.void)
        self.theta_max = 75. * math.pi / 180.
        # CLIC CDR Table 5.3.
        # using our definition of theta (equal to zero at eta=0)
        # first line added by hand for small angles,
        # with a bad resolution.
        # these tracks will not be accepted anyway,
        # but please pay attention to the acceptance method.
        self.resmap = [ (90, 8.2e-2, 9.1e-2),  
                        (80, 8.2e-4, 9.1e-3),
                        (30, 9.9e-5, 3.8e-3),
                        (20, 3.9e-5, 1.6e-3),
                        (10, 2e-5, 7.2e-4) ]  

    def acceptance(self, track):
        '''Returns True if the track is seen.
        
        Currently taken from
        https://indico.cern.ch/event/650053/contributions/2672772/attachments/1501093/2338117/FCCee_MDI_Jul30.pdf

        Original values for CLIC:
        Acceptance from the CLIC CDF p107, Fig. 5.12 without background.
        The tracker is taken to be efficient up to theta = 80 degrees. 
        '''
        pt = track.p3().Pt()
        theta = abs(track.theta())
        if theta < self.theta_max:
            if pt < 0.1:
                return False
            elif pt < 0.3:
                return random.uniform(0,1) < 0.9
            elif pt < 1:
                return random.uniform(0,1) < 0.95
            else:
                return random.uniform(0,1) < 0.99
        return False

    def _sigmapt_over_pt2(self, a, b, pt):
        '''CLIC CDR Eq. 5.1'''
        return math.sqrt( a ** 2 + (b / pt) ** 2)           

    def resolution(self, track):
        '''Returns relative resolution on the track momentum
        
        CLIC CDR, Table 5.3
        '''
        pt = track.p3().Pt()
        # matching the resmap defined above.
        theta = abs(track.theta()) * 180 / math.pi
        the_a, the_b = None, None
        for maxtheta, a, b in reversed(self.resmap):
            if theta < maxtheta:
                the_a, the_b = a, b
                break
        res = self._sigmapt_over_pt2(the_a, the_b, pt) * pt
        return res

    

class Field(DetectorElement):

    def __init__(self, magnitude):
        self.magnitude = magnitude
        volume = VolumeCylinder('field', 4.8, 5.3)
        mat = material.void
        super(Field, self).__init__('tracker', volume,  mat)


class BeamPipe(DetectorElement):
    '''Beam pipe is not used in the simulation at the moment, so no real need to define it.'''

    def __init__(self):
        #Material Seamless AISI 316 LN, External diameter 53 mm, Wall thickness 1.5 mm (hors CLIC) X0 1.72 cm
        #in CLIC, radius 25 mm (?), tchikness 8mm, X0 35.28 cm : berylluim
        factor = 1.0
        volume = VolumeCylinder('beampipe', 2.5e-2*factor+0.8e-3, 1.98, 2.5e-2*factor, 1.9785 )
        mat = material.Material('BeamPipe', 35.28e-2, 0)
        super(BeamPipe, self).__init__('beampipe', volume, mat)

        
class CLIC(Detector):
        
    def electron_acceptance(self, track):
        '''returns True if electron is seen.
        
        No information, cooking something up.
        '''
        if track.p3().Mag() > 5 and \
           abs(track.theta()) < 80. * math.pi / 180.:
            return random.uniform(0, 1) < 0.95
        else:
            return False

    def electron_resolution(self, ptc):
        '''returns the relative electron resolution.
        
        The CLIC CDR does not give any value for the electron resolution.
        We simply use the ECAL resolution.
        '''
        return self.elements['ecal'].energy_resolution(ptc.e(), ptc.eta())
            
    def muon_acceptance(self, track):
        '''returns True if muon is seen.
        
        The CLIC CDR gives 99% for E > 7.5GeV and polar angle > 10 degrees
        '''
        return track.p3().Mag() > 7.5 and \
               abs(track.theta()) < 80. * math.pi / 180.
            
    def muon_resolution(self, ptc):
        '''returns the relative muon resolution.
        
        In CLIC, the momentum resolution of the tracker is excellent and,
        due to the large amount of material before the muon chambers,
        the muon chambers cannot improve the resolution in the energy domain of FCCee.
        Therefore, using the momentum resolution of the tracker (CLIC CDR, section 8.1.1)
        '''
        return self.elements['tracker'].resolution(ptc)
    
    def ip_resolution(self, ptc):
        '''Not used yet'''
        pass
    
    def __init__(self):
        super(CLIC, self).__init__()
        self.elements['tracker'] = Tracker()
        self.elements['ecal'] = ECAL()
        self.elements['hcal'] = HCAL()
        # field limited to 2 T for FCC-ee 
        self.elements['field'] = Field(2.)
        self.elements['beampipe'] = BeamPipe()

clic = CLIC()
