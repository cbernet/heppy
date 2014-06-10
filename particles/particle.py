
class Particle(object):
    '''Base particle class.

    charge, pdg_id, p4
    print special method for subclasses
    '''
    
    def __init__(self, charge, pdg_id, p4):
        self.charge = charge
        self.pdg_id = pdg_id
        self.p4 = p4
        
    def __str__(self):
        tmp = '{className} : {pdgId:>3}, pt = {pt:5.1f}, eta = {eta:5.2f}, phi = {phi:5.2f}, mass = {mass:5.2f}'
        return tmp.format( className = self.__class__.__name__,
                           pdgId = self.pdg_id,
                           pt = self.p4.Pt(),
                           eta = self.p4.Eta(),
                           phi = self.p4.Phi(),
                           mass = self.p4.M() )
    

if __name__ == '__main__':
    from ROOT import TLorentzVector
    import math

    lv = TLorentzVector(0, 20, 50, math.sqrt(20*20+50*50))
    photon = Particle(0, 22, lv)
    print photon
