'''Global heppy configuration parameters'''

class Collider(object):
    '''Describes the collider parameters:
    
    @param BEAMS: 'pp' (default), 'ee', or 'ep'
           In the ee case, particles are sorted according to
           their energy, and theta is used in place of eta.
           In the other cases, particles are sorted according to
           their transverse momentum, and eta is used in place
           of theta
           
    @param SQRTS: Centre-of-mass energy in GeV, 13000 GeV by default.
    '''
    BEAMS = 'pp' 
    SQRTS = 13000.
