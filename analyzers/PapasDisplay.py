'''Analyzer to plot a Papas Event'''
from functools import partial
from heppy.framework.analyzer import Analyzer
from heppy.display.core import Display
from heppy.display.geometry import GDetector
from heppy.display.pfobjects import GTrajectories, Blob
#todo document arguments
#save

class PapasDisplay(Analyzer):
    '''Plots a PAPAS event display
    
    Can be used to produce a single event plot or a comparative event plot.

    Example configuration:
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
    '''

    def __init__(self, *args, **kwargs):
        super(PapasDisplay, self).__init__(*args, **kwargs)
        self.is_display = self.cfg_ana.display
        self.compare= False
        nscreens = len(self.cfg_ana.screennames)
        if (nscreens==2):
            self.compare= True         
        if (len(self.cfg_ana.particles_type_and_subtypes) != nscreens or
            len(self.cfg_ana.clusters_type_and_subtypes) != nscreens):
            raise Exception("Inconsistent display options: screennames, particles_type_and_subtypes and clusters_type_and_subtypes argument lists must have same length")
        if self.is_display:
            self.init_display()
            
    def init_display(self):
        '''Set up the display'''
        self.display = Display(self.cfg_ana.projections, self.cfg_ana.screennames)
        self.gdetector = GDetector(self.cfg_ana.detector)
        self.display.register(self.gdetector, layer=0, clearable=False)
        self.is_display = True
        

    def process(self, event):
        '''Selects the required particles and clusters and registers them on the display
        @param event: event that must contain a papasevent'''
        if not self.is_display:
            return
        self.display.clear()
        for i in range(len(self.cfg_ana.screennames)):
            particles = event.papasevent.get_collection(self.cfg_ana.particles_type_and_subtypes[i]).values()
            self.register_particles(particles, i)
            for type_and_subtype in self.cfg_ana.clusters_type_and_subtypes[i]:
                clusters = event.papasevent.get_collection(type_and_subtype).values()
                self.register_clusters(clusters, i)
 
    def register_particles(self, particles, side = 0):
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
        self.display.register(blobs, layer=2, clearable=False, sides=[side])  
        if self.compare:
            otherside = (side + 1)%2
            mapfunc = partial(Blob, grey=True)
            blobs = map(mapfunc, clusters)   
            self.display.register(blobs, layer=1, clearable=False, sides=[otherside])

