import unittest

from path import Helix
from ROOT import TLorentzVector, TVector3
from heppy.utils.computeIP import compute_IP
import numpy as np
import math
import copy

class TestPath(unittest.TestCase):
    
    def test_ip_simple(self):
        '''This simple test works for all three methods'''
        # goes along x
        p4 = TLorentzVector(1, 0, 0, 1.1)
        # starts at y = 0.1
        vertex = TVector3(0, 0.1, 0)
        helix = Helix(1, 1, p4, vertex)
        # global origin
        origin = TVector3(0, 0, 0)
        # Lucas' calculation
        ip = helix.compute_IP(origin, p4.Vect())
        self.assertAlmostEqual(ip, 0.1, places=8)
        # Nicolo's calculation
        ip2 = compute_IP(helix, origin, p4.Vect())
        self.assertAlmostEqual(ip2, 0.1, places=8)
        # and a hybrid one
        ip3 = helix.compute_IP_2(origin, p4.Vect())
        self.assertAlmostEqual(ip3, 0.1, places=8)
        
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
            ip_mine = helix.compute_IP_2(origin, smom)
            ip_nic = compute_IP(helix, origin, smom)
            ip_luc = helix.compute_IP(origin, smom)
            nplaces = 8
            self.assertAlmostEqual(abs(ip_luc), radius, places=nplaces)
            #COLIN in the following, I modify Nic's minimization args
            # so that they work, and to reach Lucas' precision
            # it works with nplaces = 5 though.
            self.assertAlmostEqual(abs(ip_mine), radius, places=nplaces)
            #COLIN: Nicolo's minimization does not give the right result
            # could be that it only works for very small distances? 
            # self.assertAlmostEqual(abs(ip2), radius, places=nplaces)
##            print math.cos(angle), math.sin(angle), radius
##            ip_pos.Print()
##            delta.Print()
##            helix_vertex.Print()
##            smom.Print()
##            helix.IP_vector.Print()
            print 'mine', ip_mine, 'nic', ip_nic, 'luca', ip_luc, radius
##            print
            
            
    
            
        
if __name__ == '__main__':
    unittest.main()
