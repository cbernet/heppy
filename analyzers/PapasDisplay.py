'''Analyzer to plot a Papas Event'''
from heppy.framework.analyzer import Analyzer
from heppy.display.core import Display
from heppy.display.geometry import GDetector
from heppy.display.pfobjects import GTrajectories, Blob


class PapasDisplay(Analyzer):
    '''Plots a PAPAS event display

    Example configuration:

    from heppy.analyzers.PapasDisplay import PapasDisplay
    papasdisplay = cfg.Analyzer(
        PapasDisplay,
        instance_label = 'papas',
        detector = detector,
        particles = 'papas_sim_particles',
        clusters = ['ecal_clusters', 'hcal_clusters']
        display = True
        )
    '''

    def __init__(self, *args, **kwargs):
        super(PapasDisplay, self).__init__(*args, **kwargs)
        self.detector = self.cfg_ana.detector
        self.is_display = self.cfg_ana.display
        if self.is_display:
            self.init_display()

    def init_display(self):
        self.display = Display(self.cfg_ana.projections, self.cfg_ana.screennames)
        self.gdetector = GDetector(self.detector)
        self.display.register(self.gdetector, layer=0, clearable=False)
        self.is_display = True

    def process(self, event):
        particles = event.papasevent.get_collection(self.cfg_ana.particles_type_and_subtype)
        if self.is_display:
            self.display.clear()
            self.display.register(GTrajectories(particles), layer=1)
            for type_and_subtype in self.cfg_ana.clusters_type_and_subtypes:
                blobs = map(Blob, event.papasevent.get_collection(type_and_subtype).values())   
                self.display.register(blobs, layer=1, clearable=False)
        self.display.draw()
