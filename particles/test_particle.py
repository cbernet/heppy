import unittest
import copy
from heppy.particles.tlv.particle import Particle as TlvParticle
from ROOT import TLorentzVector


class TestParticle(unittest.TestCase):
    
    def test_root_particle_copy(self):
        ptc = TlvParticle(1, 1, TLorentzVector())
        ptc2 = copy.deepcopy(ptc)
        self.assertEqual(ptc, ptc2)

if __name__ == '__main__':
    unittest.main()
