from pfinput import PFInput
from merger import merge_clusters
from links import Links
from distance import distance
from pfreconstructor import PFReconstructor

#TODO: this class and PFInput should probably be in the fastsim module, to try to keep the pfalgo package independent from the dataformat in use. 

class PFSequence(object):
    
    def __init__(self, simptcs, detector, logger):
        self.logger = logger
        self.recptcs = self.reconstruct(simptcs, detector)

    def reconstruct(self, simptcs, detector):
        self.pfinput = PFInput(simptcs)
        elements = self.pfinput.element_list()
        elements = merge_clusters(elements, 'hcal_in')
        elements = merge_clusters(elements, 'ecal_in')
        self.links = Links(elements, distance)
        self.pfreco = PFReconstructor( self.links, detector, self.logger)
        # print self.pfreco


if __name__ == '__main__':
    
    import shelve

    db = shelve.open('bad_photon')
    ptcs = db['ptcs']
    
    import logging
    logging.basicConfig(level='INFO')
    logger = logging.getLogger('Simulator')
    from heppy.fastsim.detectors.CMS import CMS
    detector = CMS()
    
    pfsequence = PFSequence(ptcs, detector, logger)
    particles = pfsequence.pfreco.particles

    for p in particles:
        print p 
