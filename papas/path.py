import math
from scipy import constants
from ROOT import TVector3
from heppy.utils.deltar import deltaPhi
from collections import OrderedDict

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
        z = self.vz() * time + self.origin.Z()
        x = self.origin.X() + \
            self.v_over_omega.Y() * (1-math.cos(self.omega*time)) \
            + self.v_over_omega.X() * math.sin(self.omega*time)
        y = self.origin.Y() - \
            self.v_over_omega.X() * (1-math.cos(self.omega*time)) \
            + self.v_over_omega.Y() * math.sin(self.omega*time)
        return TVector3(x, y, z)
    
    def path_length(self, deltat):
        '''ds2 = dx2+dy2+dz2 = [w2rho2 + vz2] dt2'''
        return math.sqrt(self.omega**2 * self.rho**2 + self.vz()**2)*deltat

    # def deltat(self, path_length):
    #     #TODO: shouldn't this just use beta????
    #     d1 = path_length / (self.p4.Beta()*constants.c)
    #     # d2 = path_length / math.sqrt(self.omega**2 * self.rho**2 + self.vz()**2)
    #     return d1
        
    
if __name__ == '__main__':

    from ROOT import TLorentzVector, TVector3
    p4 = TLorentzVector()
    p4.SetPtEtaPhiM(1, 0, 0, 5.11e-4)
    helix = Helix(3.8, 1, p4, TVector3(0,0,0))
    length = helix.path_length(1e-9)
    helix.deltat(length)
