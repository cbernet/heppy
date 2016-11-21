'''Particle gun, handy for testing'''

from heppy.framework.analyzer import Analyzer
from heppy.papas.pdt import particle_data
from heppy.particles.tlv.particle import Particle as TlvParticle
#TODO remove dependency to papas
from heppy.papas.pfobjects import Particle as PapasParticle #so that Gun can be used in papas (needs uniqueid)
from ROOT import TVector3

import math
import heppy.statistics.rrandom as random

from ROOT import TLorentzVector

def particle(pdgid, thetamin, thetamax, ptmin, ptmax,
             flat_pt=False, papas = False,
             phimin=-math.pi, phimax=math.pi):
    '''Create and return a particle in a given phase space
    
    @param pdgid: the pdg ID code
    @param thetamin: min theta
    @param thetamax: max theta
    @param ptmin: min pt
    @param ptmax: max pt
    @param flat_pt: False by default, indicating that the pt of the
       particle should be chosen from a uniform distribution between
       ptmin and ptmax. if set to true,
       the energy of the particle is drawn from a uniform distribution
       between ptmin and ptmax (then considered as Emin and Emax).
    '''
    mass, charge = particle_data[pdgid]
    theta = random.uniform(thetamin, thetamax)
    phi = random.uniform(phimin, phimax)
    energy = random.uniform(ptmin, ptmax)
    costheta = math.cos(math.pi/2. - theta)
    sintheta = math.sin(math.pi/2. - theta)
    tantheta = sintheta / costheta
    cosphi = math.cos(phi)
    sinphi = math.sin(phi) 
    vertex = TVector3(0,0,0)
    if flat_pt:
        pt = energy
        momentum = pt / sintheta
        energy = math.sqrt(momentum**2 + mass**2)
    else:
        energy = max([energy, mass])
        momentum = math.sqrt(energy**2 - mass**2)
    tlv = TLorentzVector(momentum*sintheta*cosphi,
                         momentum*sintheta*sinphi,
                         momentum*costheta,
                         energy)
    if papas:
        return PapasParticle(tlv, vertex, charge, pdgid, subtype ='g') #pfobjects has a uniqueid
    else:
        return TlvParticle(pdgid, charge, tlv) #pfobjects has a uniqueid    
    

class Gun(Analyzer):
    '''Particle gun.
    
    Example::
    
        from heppy.analyzers.Gun import Gun
        source = cfg.Analyzer(
            Gun,
            pdgid = 211,
            thetamin = -1.5,
            thetamax = 1.5,
            phimin = 0,
            phimax = 0.1,
            ptmin = 0,
            ptmax = 100,
            flat_pt = False,
            papas = True
        )

    @param pdgid: the pdg ID code
    @param thetamin: min theta
    @param thetamax: max theta
    @param phimin: min phi (-pi by default)
    @param phimax: max phi (+pi by default)
    @param ptmin: min pt
    @param ptmax: max pt
    @param flat_pt: False by default, indicating that the pt of the
       particle should be chosen from a uniform distribution between
       ptmin and ptmax. if set to true,
       the energy of the particle is drawn from a uniform distribution
       between ptmin and ptmax (then considered as Emin and Emax).

    '''

    def beginLoop(self, setup):
        self.papas = False
        if hasattr(self.cfg_ana, 'papas'):
            self.papas = self.cfg_ana.papas
        if not hasattr(self.cfg_ana.pdgid, '__iter__'):
            self.cfg_ana.pdgid = [self.cfg_ana.pdgid]
            
    
    def process(self, event):
        '''process event.
        
        
        creates two identical collections:
          - event.gen_particles: collection of gen particles
          - event.gen_particles_stable: collection of stable gen particles.
        '''
        if not (self.cfg_ana.pdgid, '__iter__'):
            self.cfg_ana.pdgid = [self.cfg_ana.pdgid]
        event.gen_particles = []
        for pdgid in self.cfg_ana.pdgid:
            event.gen_particles.append(particle(pdgid, 
                                                self.cfg_ana.thetamin, 
                                                self.cfg_ana.thetamax,
                                                self.cfg_ana.ptmin, 
                                                self.cfg_ana.ptmax,
                                                flat_pt=self.cfg_ana.flat_pt,
                                                papas = self.papas, 
                                                phimin=self.cfg_ana.phimin, 
                                                phimax=self.cfg_ana.phimax 
                                                ))
        event.gen_particles_stable = event.gen_particles
