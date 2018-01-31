'''CLIC-ILD model

Physics and Detectors at CLIC:
https://arxiv.org/abs/1202.5940

'''

from detector import Detector, DetectorElement
import material as material
from geometry import VolumeCylinder
import math
import heppy.statistics.rrandom as random

class ECAL(DetectorElement):

    max_radius = 4.8
    min_radius = 2.15
    max_z = 3.4
    min_z = 1.8

    def __init__(self):
        depth = 0.25
        min_radius = self.__class__.min_radius
        min_z = self.__class__.min_z
        inner_endcap_radius = 0.25
        self.maxeta = -math.log(math.tan(math.atan(inner_endcap_radius/1.7) / 2.))
        nX0 = 23  #CLIC CDR, page 70, value for CLIC_ILD
        nLambdaI = 1  # ibid
        outer_radius = min_radius + depth
        outer_z = min_z + depth
        X0 = depth / nX0
        lambdaI = depth / nLambdaI
        volume = VolumeCylinder('ecal', outer_radius, outer_z, min_radius, min_z)
        mat = material.Material('ECAL', X0, lambdaI)
        # todo: recompute
        self.eta_junction = volume.inner.eta_junction()
        # cooking up thresholds. a HG calo must be quite sensitive
        self.emin = {'barrel':0.2, 'endcap':0.2}
        # CLIC CDR p.123
        self.eres = {'barrel':[0.167, 0.0, 0.011]}
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
        elif eta < self.maxeta:
            return energy>self.emin['endcap']
        else:
            return False

    def space_resolution(self, ptc):
        pass
    
    
class HCAL(DetectorElement):

    max_radius = 4.8
    min_radius = 2.4
    max_z = 3.4
    min_z = 1.8
    
    def __init__(self):
        volume = VolumeCylinder('hcal',
                                self.__class__.max_radius, self.__class__.max_z,
                                self.__class__.min_radius, self.__class__.min_z)
        # not sure about X0 and lambda_i, but these don't matter anyway
        mat = material.Material('HCAL', 0.018, 0.17)
        # resolution from CLIC CDR Fig. 6.11, 2nd hypothesis (simple software compensation)
        self.eres = [0.5, 0.5, 0.0234]        
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
        '''
        return 0.10

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
                                      VolumeCylinder('tracker', ECAL.min_radius , ECAL.min_z),
                                      material.void)
        self.theta_max = 75. * math.pi / 180.
        # Emilia Leogrande
        # using our definition of theta (equal to zero at eta=0)
        self.resmap = [(80.0, [0.00064001464571871076, 0.13554521466257508, 1.1091870672607593]),
                       (60.0, [7.9414367183119937e-05, 0.014845686639308672, 1.0821694803464048]),
                       (40.0, [4.8900068724976152e-05, 0.0056580423053257511, 1.0924861152630758]),
                       # setting max angle of last line to 20 so that it's used. 
                       (20.0, [3.959021523612684e-05, 0.0028148305792289668, 1.0362271035102992])]



    def acceptance(self, track):
        '''Returns True if the track is seen.
        
        Currently taken from
        https://indico.cern.ch/event/650053/contributions/2672772/attachments/1501093/2338117/FCCee_MDI_Jul30.pdf

        Original values for CLIC:
        Acceptance from the CLIC CDF p107, Fig. 5.12 without background.
        The tracker is taken to be efficient up to theta = 80 degrees. 
        '''
        rnd = random.uniform(0,1)
        pt = track.p3().Pt()
        theta = abs(track.theta())
        if theta < self.theta_max:
            if pt < 0.1:
                return False
            elif pt < 0.3:
                return rnd < 0.9
            elif pt < 1:
                return rnd < 0.95
            else:
                return rnd < 0.99
        return False

    def _sigpt_over_pt2(self, x, a, b, c):
        return math.sqrt( a ** 2 + (b / x**c) ** 2 )

    def resolution(self, track):
        '''Returns relative resolution on the track momentum
        '''
        pt = track.p3().Pt()
        # matching the resmap defined above.
        theta = abs(track.theta()) * 180 / math.pi
        the_pars = None
        for maxtheta, pars in reversed(self.resmap):
            if theta < maxtheta:
                the_pars = pars 
                break
        res = 0.1  # default, for particles out of the resmap 
        if the_pars:
            res = self._sigpt_over_pt2(pt, *the_pars) * pt
        return res

    

class Field(DetectorElement):

    def __init__(self, magnitude):
        self.magnitude = magnitude
        volume = VolumeCylinder('field', HCAL.max_radius, HCAL.max_z)
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

    def electron_resolution(self, track):
        '''returns the relative electron resolution.
        
        The CLIC CDR does not give any value for the electron resolution.
        We simply use the tracker resolution as for muons
        (very thin tracker, low electron energy, low ECAL resolution w/r to CMS)
        '''
        return self.elements['tracker'].resolution(track)
            
    def muon_acceptance(self, track):
        '''returns True if muon is seen.
        
        The CLIC CDR gives 99% for E > 7.5GeV and polar angle > 10 degrees
        '''
        return track.p3().Mag() > 7.5 and \
               abs(track.theta()) < 80. * math.pi / 180.
            
    def muon_resolution(self, track):
        '''returns the relative muon resolution.
        
        In CLIC, the momentum resolution of the tracker is excellent and,
        due to the large amount of material before the muon chambers,
        the muon chambers cannot improve the resolution in the energy domain of FCCee.
        Therefore, using the momentum resolution of the tracker (CLIC CDR, section 8.1.1)
        '''
        return self.elements['tracker'].resolution(track)
    
    def ip_resolution(self, ptc):
        '''Not used yet'''
        pass

    def jet_energy_correction(self, jet):
        '''No jet energy correction for now, returning 1.'''
        return 1.
    
    def __init__(self):
        super(CLIC, self).__init__()
        self.elements['tracker'] = Tracker()
        self.elements['ecal'] = ECAL()
        self.elements['hcal'] = HCAL()
        # field limited to 2 T for FCC-ee 
        self.elements['field'] = Field(2.)



clic = CLIC()
