import unittest
import numpy as np
import math
import copy
from heppy.particles.tlv.resonance import Resonance2 as Resonance
from heppy.particles.tlv.particle import Particle
from ROOT import TLorentzVector, TVector3

def acop_patrick(leg1, leg2):
    '''
    Information sent by Patrick
    vect1 = TVector3(self.jets[0].px(), self.jets[0].py(), self.jets[0].pz())
    vect2 = TVector3(self.jets[1].px(), self.jets[1].py(), self.jets[1].pz())
    cross = vect1.Unit().Cross(vect2.Unit())
    # looks bugged, cross is not a unit vector
    cross = abs(cross.z())
    cross = asin(cross) * 180./pi
    '''
    cross = leg1.p3().Unit().Cross(leg2.p3().Unit())
    cross = abs(cross.Z())
    cross = math.asin(cross)*180./math.pi
    # cross = math.asin(cross)
    return cross

class TestResonance(unittest.TestCase):
    
    def test_many(self):        
        nzeds = 100
        masses = np.linspace(80, 100, nzeds)
        boosts = np.linspace(1, 50, nzeds)
        thetas = np.linspace(1, math.pi, nzeds)
        for mass, boost, theta in zip(masses, boosts, thetas):
            energy = mass / 2.
            ptc1 = Particle(11, -1,
                            TLorentzVector(0, energy, 0, energy))
            ptc2 = Particle(11, 1,
                            TLorentzVector(0, -energy, 0, energy))
            resonance = Resonance(ptc1, ptc2, 23)
            p3_lab = TVector3()
            p3_lab.SetMagThetaPhi(boost, theta, 0.1)
            p4_lab = TLorentzVector()
            p4_lab.SetVectM(p3_lab, mass)
            bp4 = copy.deepcopy(resonance.p4())
            boost_vector = p4_lab.BoostVector()
            bp4.Boost(boost_vector)
            places = 8
            self.assertAlmostEqual(bp4.Vect().Mag(), boost, places)
            self.assertAlmostEqual(bp4.M(), mass, places)
            resonance.boost(boost_vector)
            self.assertAlmostEqual(bp4.E(), resonance.e(), places)

    def test_resonance(self):
        ptc1 = Particle(11, -1, TLorentzVector(1, 0, 0, 1))
        ptc2 = Particle(-11, 1, TLorentzVector(2, 0, 0, 2))
        reso = Resonance( ptc1, ptc2, 23 )
        self.assertEqual( reso._pid, 23 )
        self.assertEqual( reso.e(), 3 )
        self.assertEqual( reso.leg1(), ptc1 )
        self.assertEqual( reso.leg2(), ptc2 )
        self.assertEqual( reso.q(), 0 )
        self.assertEqual( reso.p4(), TLorentzVector(3,0,0,3) )

    def test_acoplanarity(self):
        '''test acoplanarity w/r to Patricks implementation
        '''
        ptc1 = Particle(11, -1, TLorentzVector(1, 2, 3, 7))
        ptc2 = Particle(-11, 1, TLorentzVector(2, 3, 4, 10))
        reso = Resonance( ptc1, ptc2, 23 )
        self.assertEqual(reso.cross(),
                         acop_patrick(reso.leg1(), reso.leg2()))
        

if __name__ == '__main__':
    unittest.main()
