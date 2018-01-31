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
        self.assertAlmostEqual(abs(ip2), self.true_IP, places=5)
        # and a hybrid one
##        ip3 = self.helix.compute_IP_2(self.origin, self.p4.Vect())
##        self.assertAlmostEqual(ip3, self.true_IP, places=8)
        
    def test_ip_many(self):
        npoints = 100
        scale = 1e-6
        radii = np.linspace(0.1*scale, 0.2*scale, npoints)
        angles = np.linspace(0, math.pi, npoints)
        momenta = np.linspace(200, 500, npoints)
        mass = 0.5
        field = 1e-5
        origin = TVector3(0, 0, 0)
        for radius, angle, momentum in zip(radii, angles, momenta):
            ip_pos = TVector3(math.cos(angle), math.sin(angle), 0)
            ip_pos *= radius
            p3 = TVector3(math.cos(angle-math.pi/2.),
                            math.sin(angle-math.pi/2.), 0)
            p3 *= momentum
            p4 = TLorentzVector()
            p4.SetVectM(p3, mass)
            helix_vertex = copy.deepcopy(ip_pos)
            delta = copy.deepcopy(p3.Unit())
            delta *= radius
            helix_vertex += delta
            helix = Helix(field, 1., p4, helix_vertex)
            # jet direction is 0.1 radians away from particle direction
            # to obtain a positivive IP sign
            jet_dir = copy.deepcopy(p3).Unit()
            jet_dir.RotateZ(0.1)
            ip_nic = compute_IP(helix, origin, jet_dir)
            ip_obj = ImpactParameter(helix, origin, jet_dir)
            verbose = False
            places = 8
            if verbose:
                print '-' * 50
                print math.cos(angle), math.sin(angle), radius
                print 'obj', ip_obj.value, '({})'.format(abs(ip_obj.value)-radius)
                print 'nic', ip_nic, '({})'.format(abs(ip_nic)-radius) 
            else:
                self.assertAlmostEqual(abs(ip_obj.value), radius, places=places)
                #COLIN->NIC: Nicolo's minimization does not give the right result
                # could be that it only works for very small distances?
                # can be tested by uncommenting the following line and
                # running this test file
                self.assertAlmostEqual(abs(ip_nic), radius, places=places)
    
    def test_ipclass(self):
        self.p4.Vect().Print()
        ip = ImpactParameter(self.helix, self.origin, self.p4.Vect())
        self.assertAlmostEqual(ip.value, self.true_IP, places=5)
        
if __name__ == '__main__':
    unittest.main()
