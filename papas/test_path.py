import unittest

from path import Helix, ImpactParameter
from heppy.analyzers.ImpactParameterSmearer import smear_IP
from ROOT import TLorentzVector, TVector3
from heppy.utils.computeIP import compute_IP
import numpy as np
import math
import copy

class TestPath(unittest.TestCase):        
    
    def setUp(self):
        # goes along x
        self.p4 = TLorentzVector(1, 0, 0, 1.1)
        # starts at y = 0.1
        self.true_IP = 0.1
        self.vertex = TVector3(0, self.true_IP, 0)
        self.helix = Helix(1, 1, self.p4, self.vertex)
        # global origin
        self.origin = TVector3(0, 0, 0)
    
    def test_ip_simple(self):
        '''This simple test works for all three methods'''
        # Lucas' calculation
##        ip = self.helix.compute_IP(self.origin, self.p4.Vect())
##        self.assertAlmostEqual(ip, self.true_IP, places=8)
        # Nicolo's calculation
        ip2 = compute_IP(self.helix, self.origin, self.p4.Vect())
        self.assertAlmostEqual(ip2, self.true_IP, places=8)
        # and a hybrid one
##        ip3 = self.helix.compute_IP_2(self.origin, self.p4.Vect())
##        self.assertAlmostEqual(ip3, self.true_IP, places=8)
        
    def test_ip_many(self):
        npoints = 100
        radii = np.linspace(0.1, 0.2, npoints)
        angles = np.linspace(0, math.pi, npoints)
        momenta = np.linspace(200, 500, npoints)
        mass = 0.5
        field = 1e-5
        origin = TVector3(0, 0, 0)
        for radius, angle, momentum in zip(radii, angles, momenta):
            ip_pos = TVector3(math.cos(angle), math.sin(angle), 0)
            ip_pos *= radius
            smom = TVector3(math.cos(angle-math.pi/2.),
                            math.sin(angle-math.pi/2.), 0)
            smom *= momentum
            p4 = TLorentzVector()
            p4.SetVectM(smom, mass)
            helix_vertex = copy.deepcopy(ip_pos)
            delta = copy.deepcopy(smom.Unit())
            delta *= radius
            helix_vertex += delta
            helix = Helix(field, 1., p4, helix_vertex)
##            ip_mine = helix.compute_IP_2(origin, smom)
            ip_nic = compute_IP(helix, origin, smom)
##            ip_luc = helix.compute_IP(origin, smom)
            ip_obj = ImpactParameter(helix, origin, smom)
            nplaces = 8
##            self.assertAlmostEqual(abs(ip_luc), radius, places=nplaces)
            #COLIN->NIC in the following, I modify Nic's minimization args
            # so that they work, and to reach Lucas' precision
            # it works with nplaces = 5 though.
##            self.assertAlmostEqual(abs(ip_mine), radius, places=nplaces)
            self.assertAlmostEqual(abs(ip_obj.value), radius, places=nplaces)
            #COLIN->NIC: Nicolo's minimization does not give the right result
            # could be that it only works for very small distances?
            # can be tested by uncommenting the following line and
            # running this test file
            # self.assertAlmostEqual(abs(ip2), radius, places=nplaces)
##            print math.cos(angle), math.sin(angle), radius
##            ip_pos.Print()
##            delta.Print()
##            helix_vertex.Print()
##            smom.Print()
##            helix.IP_vector.Print()
##            print 'mine', ip_mine, 'nic', ip_nic, 'luca', ip_luc, radius
##            print
            
            
##    def test_smear(self):
##        self.helix.IP_resolution = 1
##        self.helix.compute_IP_2(self.origin, self.p4.Vect())
##        smear_IP(self.helix, -1, -1)
    
    def test_ipclass(self):
        self.p4.Vect().Print()
        ip = ImpactParameter(self.helix, self.origin, self.p4.Vect())
        self.assertAlmostEqual(ip.value, self.true_IP, places=8)
        
if __name__ == '__main__':
    unittest.main()
