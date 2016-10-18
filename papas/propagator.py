from vectors import Point
import math
import copy
from ROOT import TVector3
from geotools import circle_intersection
from papas_exceptions import PropagationError
from path import Helix, StraightLine, Info


class Propagator(object):

    def propagate(self, particles, cylinders, *args, **kwargs):
        for ptc in particles:
            for cyl in cylinders:
                self.propagate_one(ptc, cyl, *args, **kwargs)
 
class StraightLinePropagator(Propagator):        

    def propagate_one(self, particle, cylinder, dummy=None):
        line = StraightLine(particle.p4(), particle.vertex) 
        particle.set_path( line ) # TODO 
        position = line.position(cylinder, dummy)
        if position==None:
            return
        particle.points[cylinder.name] = position 
  
class HelixPropagator(Propagator):
    
    def propagate_one(self, particle, cylinder, field, debug_info=None):
        helix = Helix(field, particle.q(), particle.p4(), particle.vertex)
        particle.set_path(helix)
        destination=helix.destination(cylinder)  
        if destination == None:
            return
        particle.points[cylinder.name] = destination['position']
        return destination['info']
 
straight_line = StraightLinePropagator()
helix = HelixPropagator() 
