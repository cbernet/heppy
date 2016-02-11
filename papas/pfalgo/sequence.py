from pfinput import PFInput
from merger import merge_clusters
from links import Links
from distance import distance
from pfreconstructor import PFReconstructor

#TODO: this class and PFInput should probably be in the papas module, to try to keep the pfalgo package independent from the dataformat in use. 

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


