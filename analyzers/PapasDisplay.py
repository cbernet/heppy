'''Analyzer to plot a Papas Event'''
from heppy.framework.analyzer import Analyzer
from heppy.display.core import Display
from heppy.display.geometry import GDetector
from heppy.display.pfobjects import GTrajectories, Blob


class PapasDisplay(Analyzer):
    '''Plots a PAPAS event display

    Example configuration::

        from heppy.analyzers.PapasDisplay import PapasDisplay
        papasdisplay = cfg.Analyzer(
            PapasDisplay,
            instance_label = 'papas',
            detector = detector,
            particles = 'papas_sim_particles',
            clusters = ['ecal_clusters', 'hcal_clusters']
            display = True
            )
            
    @param detector: the detector to be used. 
    '''

    def __init__(self, *args, **kwargs):
        super(PapasDisplay, self).__init__(*args, **kwargs)
        self.detector = self.cfg_ana.detector
        if self.cfg_ana.do_display:
            self.init_display()

    def init_display(self):
        self.display = Display(self.cfg_ana.projections, self.cfg_ana.screennames)
        self.gdetector = GDetector(self.detector)
        self.display.register(self.gdetector, layer=0, clearable=False)

    def process(self, event):
        particles = event.papasevent.get_collection(self.cfg_ana.particles_type_and_subtype)
        if self.cfg_ana.do_display:
            self.display.clear()
            self.display.register(GTrajectories(particles), layer=1)
            for type_and_subtype in self.cfg_ana.clusters_type_and_subtypes:
                coll = event.papasevent.get_collection(type_and_subtype)
                if coll:
                    blobs = map(Blob, coll.values())   
                    self.display.register(blobs, layer=1)

