from particles.pod import POD
from particles.p4 import P4

class Jet(POD, P4):
    pass

class Particle(POD, P4):
    def __str__(self):
        tmp = '{className} : id = {id:3} pt = {pt:5.1f}, eta = {eta:5.2f}, phi = {phi:5.2f}, mass = {mass:5.2f}'
        return tmp.format(
            className = self.__class__.__name__,
            id = self.ID(),
            pt = self.P4().Pt,
            eta = self.P4().Eta,
            phi = self.P4().Phi,
            mass = self.P4().Mass
            )
    

