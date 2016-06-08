import math
from scipy import constants
from numpy import sign
from ROOT import TLorentzVector, TVector3
import random

from heppy.papas.path import Helix
from heppy.papas.pfobjects import Particle

# propagate untill surface
#_______________________________________________________________________________
# find t_scat, time when scattering :

def multiple_scattering( particle, detector_element, field ):
    if not particle._charge ==0:
        
        
        # detector_element.volume.rad
        
        scat_point = particle.path.points['{}_in'.format(detector_element.name)]
        
        phi_t_scat = particle.path.phi( scat_point.X(), scat_point.Y())
        
        t_scat = particle.path.time_at_phi(phi_t_scat)
        #_______________________________________________________________________
        # compute p4_t = p4 at t_scat :
        
        p4_0 = particle.path.p4.Clone()
        p4tx = p4_0.X()*math.cos(particle.path.omega*t_scat) + p4_0.Y()*math.sin(particle.path.omega*t_scat)
        p4ty =-p4_0.X()*math.sin(particle.path.omega*t_scat) + p4_0.Y()*math.cos(particle.path.omega*t_scat)
        p4tz = p4_0.Z()
        p4tt = p4_0.T()
        p4_t = TLorentzVector(p4tx, p4ty, p4tz, p4tt)
        #particle.path.p4.RotateZ(particle.path.omega*t_scat)
        #p4_t = particle.path.p4.Clone()
        #_______________________________________________________________________
        # now, p4t will be modified with respect to the multiple scattering
        # first one has to determine theta_0 the width of the gaussian :
        P = p4_t.Vect().Dot(p4_t.Vect().Unit())
        PT= p4_t.Perp()
        thick = detector_element.volume.outer.rad-detector_element.volume.inner.rad
        #  = detector_element.material.lambdaI
        x = abs(thick * 1.0* P/PT)
        X_0 = detector_element.material.x0
        # detector_element.material.x0
            
        # distance and radiation length, linked to the dectector properties
        # and the particle's direction
        
        
        # /!\ debug
        theta_0 = 1.0*13.6e-3/(1.0*particle.path.speed/constants.c*P)*abs(particle.path.charge)
        theta_0 *= (1.0*x/X_0)**(1.0/2)*(1+0.038*math.log(1.0*x/X_0))
        
        # now, make p4_t change due to scattering :
        
        theta_space = random.gauss(0, theta_0*2.0**(1.0/2))
        psi = constants.pi*random.random()
        
        p3i = p4_t.Vect().Clone()
        
        e_z = TVector3(0,0,1)
               
        #first rotation : theta, in the xy plane
        a = p3i.Cross(e_z)
        #this may change the sign, but randomly, as the sign of theta already is
        p4_t.Rotate(theta_space,a)
                
        #second rotation : psi (isotropic around initial direction)
        p4_t.Rotate(psi,p3i.Unit())

        #_______________________________________________________________________
        # creating new helix, ref at scattering point :
        helix_new_t = Helix(field, particle.path.charge, p4_t,
                            particle.path.point_at_time(t_scat))
            
        # now, back to t=0
        #particle.path.p4.RotateZ(-particle.path.omega*t_scat)
        p4sx = p4_t.X()*math.cos(-particle.path.omega*t_scat) + p4_t.Y()*math.sin(-particle.path.omega*t_scat)
        p4sy =-p4_t.X()*math.sin(-particle.path.omega*t_scat) + p4_t.Y()*math.cos(-particle.path.omega*t_scat)
        p4sz = p4_t.Z()
        p4st = p4_t.T()
        p4_scat = TLorentzVector(p4sx, p4sy, p4sz, p4st)
        
        # creating new helix, ref at new t0 point :
        helix_new_0 = Helix(field, particle.path.charge, p4_scat,
                            helix_new_t.point_at_time(-t_scat))
        
        #particle.path.p4.Clone(), origin_scat)
        #particle.p3() = helix_new_0.p4().Vect()
        particle.set_path(helix_new_0, option = 'w')
        
        
