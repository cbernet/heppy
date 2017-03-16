'''Analyzer to construct Papas Event Display plots'''
from functools import partial
from heppy.framework.analyzer import Analyzer
from heppy.display.core import Display
from heppy.display.geometry import GDetector
from heppy.display.pfobjects import GTrajectories, Blob
#todo save

class PapasDisplay(Analyzer):
    '''Plots a PAPAS event display
    
    Can be used to produce a single event plot or a comparative event plot.

    Example configuration::
        #(single event plot)
        from heppy.analyzers.PapasDisplay import PapasDisplay 
        papasdisplay = cfg.Analyzer(
           PapaDisplay,
           projections = ['xy', 'yz'],
           screennames = ["simulated"],
           particles_type_and_subtypes = ['ps'],
           clusters_type_and_subtypes = [['es', 'hs']],
           detector = detector,
           save = True,
           display = True
        )
        #(comparative event plot)
        from heppy.analyzers.PapasDisplay import PapasDisplay 
        papasdisplay = cfg.Analyzer(
           PapaDisplay,
           projections = ['xy', 'yz'],
           screennames = ["simulated", "reconstructed"],
           particles_type_and_subtypes = ['ps', 'pr'],
           clusters_type_and_subtypes = [['es', 'hs'],['em', 'hm']],
           detector = detector,
           save = True,
           display = True
        )
    
    @param projections: list of projections eg ['xy', 'yz', 'xz' ,'ECAL_thetaphi', 'HCAL_thetaphi']
                 these will be separate windows
    @param subscreens: list of names of panels within each window eg subscreens=["simulated", "reconstructed"]
          each of the projection windows will contain all of the subscreens
          the subscreens can be used to show different aspects of an event, eg simulated particles and reconstructed particles
    @param particles_type_and_subtypes: list of type_and_subtypes of particles (eg ['ps', 'pr']). 
           List must be same length as subscreens. Each element of list says which particles to plot on the corresponding subscreen.
    @param clusters_type_and_subtypes: list of type_and_subtypes of clusters (eg [['es', 'hs'],['em', 'hm']]). 
           The list must be same length as subscreens, and each element should itself be a list. 
           Each element of the list says which clusters to plot on the corresponding subscreen.
           More than one cluster type may be plotted on a single screen.
    @param detector: the detector to be plotted
    @param save: boolean, if True will save graph to png file.
    @param display: boolean, if True will plot graph to screen.
 '''


    def __init__(self, *args, **kwargs):
        super(PapasDisplay, self).__init__(*args, **kwargs)
        self.compare = False
        nscreens = len(self.cfg_ana.screennames)
        if nscreens == 2:
            self.compare = True     
        if (len(self.cfg_ana.particles_type_and_subtypes) != nscreens or
                len(self.cfg_ana.clusters_type_and_subtypes) != nscreens):
            raise Exception("Inconsistent display options: screennames, particles_type_and_subtypes and clusters_type_and_subtypes argument lists must have same length")
        if self.cfg_ana.do_display:
            self.init_display()

    def init_display(self):
        '''Set up the display'''
        self.display = Display(self.cfg_ana.projections, self.cfg_ana.screennames)
        self.gdetector = GDetector(self.cfg_ana.detector)
        self.display.register(self.gdetector, layer=0, clearable=False)

    def process(self, event):
        '''Selects the required particles and clusters and registers them on the display
        @param event: event that must contain a papasevent'''
        if not self.cfg_ana.do_display:
            return
        self.display.clear()
        for i in range(len(self.cfg_ana.screennames)):
            particles_collection = event.papasevent.get_collection(self.cfg_ana.particles_type_and_subtypes[i])
            if particles_collection:
                self.register_particles(particles_collection.values(), i)
            for type_and_subtype in self.cfg_ana.clusters_type_and_subtypes[i]:
                clusters = event.papasevent.get_collection(type_and_subtype)
                if clusters:
                    self.register_clusters(clusters.values(), i)
 
    def register_particles(self, particles, side=0):
        '''
        Adds list of particles into the display
        @param particles:  list of particles to append to display
        @param side:  0 = left, 1 = right
        '''
        self.display.register(GTrajectories(particles), layer=2, sides=[side])
        if self.compare:
            otherside = (side + 1)%2 #opposite side
            self.display.register(GTrajectories(particles, is_grey=True), layer=1, sides=[otherside])
 
    def register_clusters(self, clusters, side=0):
        '''Adds list of clusters into the display
        @param clusters:  list of clusters to append to display
        @param side:  0 = left, 1 = right'''        
        blobs = map(Blob, clusters)   
        self.display.register(blobs, layer=2, clearable=True, sides=[side])
        if self.compare:
            otherside = (side + 1)%2
            mapfunc = partial(Blob, grey=True)
            blobs = map(mapfunc, clusters)
            self.display.register(blobs, layer=1, clearable=True, sides=[otherside])
