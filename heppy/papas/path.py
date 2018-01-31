import math
from scipy import constants
from ROOT import TVector3, TLorentzVector
from heppy.utils.deltar import deltaPhi
from collections import OrderedDict
import scipy.optimize 
from numpy import sign
import heppy.statistics.rrandom as random

class Path(object):
    '''Path followed by a particle in 3D space. 
    Assumes constant speed magnitude both along the z axis and in the transverse plane.
    '''
        
    def __init__(self, p4, origin):
        self.p4 = p4
        self.udir = p4.Vect().Unit()
        self.origin = origin
        self.speed = self.p4.Beta() * constants.c
        self.points = OrderedDict()
        self.points['vertex'] = origin

    def time_at_z(self, z):
        dest_time = (z - self.origin.Z())/self.vz()
        return dest_time

    def deltat(self, path_length):
        '''Time needed to follow a given path length'''
        return path_length / self.speed

    def point_at_time(self, time):
        '''Returns the 3D point on the path at a given time'''
        return self.origin + self.udir * self.speed * time
        
    def vz(self):
        '''Speed magnitude along z axis'''
        return self.p4.Beta() * constants.c * self.udir.Z()

    def vperp(self):
        '''Speed magnitude in the transverse plane'''
        return self.p4.Beta() * constants.c * self.udir.Perp()

    
class StraightLine(Path):
    pass
    
    
class Helix(Path):
    def __init__(self, field, charge, p4, origin):
        super(Helix, self).__init__(p4, origin)
        self.charge = charge
        self.rho = p4.Perp() / (abs(charge)*field) * 1e9/constants.c
        self.v_over_omega = p4.Vect()
        self.v_over_omega *= 1./(charge*field)*1e9/constants.c
        self.omega = charge*field*constants.c**2 / (p4.M()*p4.Gamma()*1e9)
        momperp_xy = TVector3(-p4.Y(), p4.X(), 0.).Unit()
        origin_xy = TVector3(origin.X(), origin.Y(), 0.)
        self.center_xy = origin_xy - charge * momperp_xy * self.rho
        self.extreme_point_xy = TVector3(self.rho, 0, 0) 
        if self.center_xy.X()!=0 or self.center_xy.Y()!=0:
            self.extreme_point_xy = self.center_xy + self.center_xy.Unit() * self.rho
        # calculate phi range with the origin at the center,
        # for display purposes
        center_to_origin = origin_xy - self.center_xy
        self.phi0 = center_to_origin.Phi()
        self.phi_min = self.phi0 * 180 / math.pi
        self.phi_max = self.phi_min + 360.

    def polar_at_time(self, time):
        z = self.vz() * time + self.origin.Z()
        rho = self.rho
        phi = - self.omega * time + self.phi0
        return rho, z, phi

    def time_at_phi(self, phi):
        time = deltaPhi(self.phi0, phi) / self.omega
        return time

    def phi(self, x, y):
        xy = TVector3(x,y,0)
        xy -= self.center_xy
        return xy.Phi()
        
    def point_from_polar(self, polar):
        rho,z,phi = polar
        xy = self.center_xy + self.rho * TVector3(math.cos(phi), math.sin(phi), 0)
        return TVector3(xy.X(), xy.Y(), z)
        
    def point_at_time(self, time):
        '''return a TVector3 with cartesian coordinates at time t'''
        x,y,z = self.coord_at_time(time)
        return TVector3(x, y, z)
    
    def path_length(self, deltat):
        '''ds2 = dx2+dy2+dz2 = [w2rho2 + vz2] dt2'''
        return math.sqrt(self.omega**2 * self.rho**2 + self.vz()**2)*deltat
 
    def coord_at_time(self, time):
        '''returns x,y,z at time t'''
        x = self.origin.X() + \
            self.v_over_omega.Y() * (1-math.cos(self.omega*time)) \
            + self.v_over_omega.X() * math.sin(self.omega*time)
        y = self.origin.Y() - \
            self.v_over_omega.X() * (1-math.cos(self.omega*time)) \
            + self.v_over_omega.Y() * math.sin(self.omega*time)
        z = self.vz() * time + self.origin.Z()
        return x,y,z
       
    
class ImpactParameter(object):
    '''Performs impact parameter calculation, and stores relevant information.'''
    
    def __init__(self, helix, origin, jet_direction, resolution=0.):
        '''Constructs impact parameter.
        
        @param helix: the helix for which the impact parameter is
          calculated.
        @param origin: TVector3-like vertex of origin, w/r to which
          the impact parameter is calculated
        @param jet_direction: TVector3-like, necessary to calculate
          the sign of the impact parameter
        @param resolution: resolution estimate to calculate the
          impact parameter significance
        
        The impact parameter calculation involves a minimization
        performed using the brent method of scipy.optimize.minimize_scalar.
        The point of closest approach must be within -5 and +5 ns
        of the helix vertex (point of reference on the helix,
        not the primary vertex).
        
        Interesting attributes:
        - helix: the corresponding helix
        - origin: the corresponding primary vertex
        - time: the time corresponding to the point of closest approach
          on the helix
        - vector: from the origin to the point of closest approach
        - sign: impact parameter sign
        - value: impact parameter value, defined as the distance between
          the primary vertex and the point of closest approach,
          times the sign
        - significance
          impact parameter significance, defined as the value divided
          by the resolution.
        '''
        self.helix = helix
        self.origin = origin
        def distquad (time):
            x,y,z = self.helix.coord_at_time(time)
            dist2 = (x-origin.x())**2 + (y-origin.y())**2 + (z-origin.z())**2 
            return dist2
        minim_answer = scipy.optimize.minimize_scalar(
            distquad,
            method='brent', 
            bracket = [-5e-9, 5e-9],
            options={'xtol': 1e-20, 'maxiter': 1e5},
            tol=None,
        )
        self.time = minim_answer.x
        self.vector = self.helix.point_at_time(self.time) - origin
        jet_direction = jet_direction.Unit()
        self.sign  = self.vector.Dot(jet_direction)
        if self.sign == 0:
            self.sign = 1
        self.value = self.vector.Mag()*sign(self.sign)
        if resolution:
            self.significance = self.value / resolution
                        
    def __str__(self):
        def vector_desc(name, vec):
            return '{:7}\t: mag={:3.2f}, phi={:3.2f}, theta={:3.2f}'.format(
                name, vec.Mag(), vec.Phi(), vec.Theta()
            )       
        lines = [ vector_desc('origin', self.origin), 
                  vector_desc('IP', self.vector), ]
        return '\n'.join(lines)
        
        
if __name__ == '__main__':

    from ROOT import TLorentzVector, TVector3
    p4 = TLorentzVector()
    p4.SetPtEtaPhiM(1, 0, 0, 5.11e-4)
    helix = Helix(3.8, 1, p4, TVector3(0,0,0))
    length = helix.path_length(1e-9)
    helix.deltat(length)
    
