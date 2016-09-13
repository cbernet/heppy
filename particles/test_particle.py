import unittest
import os
import copy
from heppy.particles.tlv.particle import Particle as TlvParticle
from heppy.particles.fcc.particle import Particle as FccParticle
from ROOT import TLorentzVector, gSystem


class TestParticle(unittest.TestCase):
    
    def test_root_particle_copy(self):
        ptc = TlvParticle(1, 1, TLorentzVector())
        ptc2 = copy.deepcopy(ptc)
        self.assertEqual(ptc, ptc2)

    #----------------------------------------------------------------------
    def test_fcc_particle(self):
        """Test that FCC particles can be copied and compared"""
        retcode = gSystem.Load("libdatamodelDict")
        # testing only if the FCC EDM is available
        if retcode == -1:
            return
        try:
            from EventStore import EventStore as Events
        except ImportError:
            return
        test_fcc_file = '/'.join([os.environ['HEPPY'],
                                  'test/data/ee_ZH_Zmumu_Hbb.root'])
        events = Events([test_fcc_file])
        event = next(iter(events))
        fccptc = event.get('GenParticle')
        ptcs = map(FccParticle, fccptc)
        ptc0_2 = copy.deepcopy(ptcs[0])
        self.assertEqual(ptc0_2, ptcs[0])
        

if __name__ == '__main__':
    unittest.main()
