from vectors import Point
from heppy.particles.tlv.particle import Particle as BaseParticle
from heppy.utils.deltar import deltaR
import math

class PFObject(object):
    '''Base class for all particle flow objects (tracks, clusters, etc).
    Particle flow objects of different types can be linked together
    forming graphs called "blocks". 

    attributes: 
    linked : list of PFObjects linked to this one 
    locked : already used in the particle flow algorithm 
    block_label : label of the block the PFObject belongs to. The block label is a unique identifier for the block.
    ''' 
    
    def __init__(self):
        super(PFObject, self).__init__()
        self.linked = []
        self.locked = False
        self.block_label = None

    def accept(self, visitor):
        '''Called by visitors, such as FloodFill. See pfalgo.floodfill'''
        notseen = visitor.visit(self)
        if notseen:
            for elem in self.linked:
                elem.accept(visitor)

    def __repr__(self):
        return str(self)


class Cluster(PFObject):

    #TODO: not sure this plays well with SmearedClusters
    max_energy = 0.
    
    def __init__(self, energy, position, size_m, layer, particle=None):
        super(Cluster, self).__init__()
        self.position = position
        self.set_energy(energy)
        self.set_size( float(size_m) )
        self.layer = layer
        self.particle = particle
        self.subclusters = [self]
        # self.absorbed = []

    def set_size(self, value):
        self._size = value
        try:
            self._angularsize = math.atan( self._size / self.position.Mag() ) 
        except:
            import pdb; pdb.set_trace()
            
    def size(self):
        return self._size

    def angular_size(self):
        return self._angularsize

    def is_inside(self, point):
        subdists = [ (subc.position - point).Mag() for subc in self.subclusters ]
        dist = min(subdists) 
        if dist < self.size():
            return True, dist
        else:
            return False, dist

    def __iadd__(self, other):
        if other.layer != self.layer:
            raise ValueError('can only add a cluster from the same layer') 
        position = self.position * self.energy + other.position * other.energy
        energy = self.energy + other.energy
        denom  = 1/energy
        position *= denom
        self.position = position
        self.energy = energy
        self.subclusters.extend(other.subclusters)
        return self

    def set_energy(self, energy):
        energy = float(energy)
        self.energy = energy
        if energy > self.__class__.max_energy:
            self.__class__.max_energy = energy
        self.pt = energy * self.position.Unit().Perp()

    # fancy but I prefer the other solution
    # def __setattr__(self, name, value):
    #     if name == 'energy':
    #         self.pt = value * self.position.Unit().Perp()
    #     self.__dict__[name] = value

    def __str__(self):
        return '{classname:15}: {layer:10} {energy:7.2f} {theta:5.2f} {phi:5.2f}'.format(
            classname = self.__class__.__name__,
            layer = self.layer,
            energy = self.energy,
            theta = math.pi/2. - self.position.Theta(),
            phi = self.position.Phi()
        )
        
class SmearedCluster(Cluster):
    def __init__(self, mother, *args, **kwargs):
        self.mother = mother
        super(SmearedCluster, self).__init__(*args, **kwargs)

        
class Track(PFObject):
    '''Determines the trajectory in space and time of a particle (charged or neutral).

    attributes: 
    - p3 : momentum in 3D space (px, py, pz) 
    - charge : particle charge 
    - path : contains the trajectory parameters and points  
    '''
    
    def __init__(self, p3, charge, path, particle=None):
        super(Track, self).__init__()
        self.p3 = p3
        self.pt = p3.Perp()
        self.energy = p3.Mag()  #TODO clarify energy and momentum
        self.charge = charge
        self.path = path
        self.particle = particle
        self.layer = 'tracker'

    def __str__(self):
        return '{classname:15}: {e:7.2f} {pt:7.2f} {theta:5.2f} {phi:5.2f}'.format(
            classname = self.__class__.__name__,
            pt = self.pt,
            e = self.energy, 
            theta = math.pi/2. - self.p3.Theta(),
            phi = self.p3.Phi()
        )
        

        
class SmearedTrack(Track):

    def __init__(self, mother, *args, **kwargs):
        self.mother = mother
        self.path = mother.path
        super(SmearedTrack, self).__init__(*args, **kwargs)
    
        
class Particle(BaseParticle):
    def __init__(self, tlv, vertex, charge, pdgid=None):
        super(Particle, self).__init__(pdgid, charge, tlv)
        self.vertex = vertex
        self.path = None
        self.clusters = dict()
        self.track = Track(self.p3(), self.q(), self.path)
        self.clusters_smeared = dict()
        self.track_smeared = None  
  
    def __getattr__(self, name):
        if name=='points':
            # if self.path is None:
            #     import pdb; pdb.set_trace()
            return self.path.points
        else:
            raise AttributeError
            
        
    def is_em(self):
        kind = abs(self.pdgid())
        if kind==11 or kind==22:
            return True
        else:
            return False
        
    def set_path(self, path, option=None):
        if option == 'w' or self.path is None:
            self.path = path
            self.track = Track(self.p3(), self.q(), self.path)

    
if __name__ == '__main__':
    from ROOT import TVector3
    cluster = Cluster(10., TVector3(1,0,0), 1, 1)
    print cluster.pt
    cluster.set_energy(5.)
    print cluster.pt
    
