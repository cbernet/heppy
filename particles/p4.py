class P4(object):

    def pt(self):
        return self.p4().pt()
    def eta(self):
        return self.p4().eta()
    def phi(self):
        return self.p4().phi()
    def mass(self):
        return self.p4().mass()
    
    def __str__(self):
        tmp = '{className} : pt = {pt:5.1f}, eta = {eta:5.2f}, phi = {phi:5.2f}, mass = {mass:5.2f}'
        return tmp.format( className = self.__class__.__name__,
                           pt = self.P4().Pt,
                           eta = self.P4().Eta,
                           phi = self.P4().Phi,
                           mass = self.P4().Mass )
    
