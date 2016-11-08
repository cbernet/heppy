
'''Analyzer to plot a Papas Event'''
from heppy.framework.analyzer import Analyzer
from heppy.display.core import Display
from heppy.display.geometry import GDetector
from heppy.display.pfobjects import GTrajectories


class PapasDisplay(Analyzer):
    '''Plots a PAPAS event

    Example configuration:

    from heppy.analyzers.PapasDisplay import PapasDisplay
    papasdisplay = cfg.Analyzer(
        PapasDisplay,
        instance_label = 'papas',
        detector = detector,
        particles = 'papas_sim_particles',
        #particles = 'papas_PFreconstruction_particles_list',
        display_filter_func = lambda ptc: ptc.e()>1.,
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
        self.display = Display(['xy', 'yz'])
        self.gdetector = GDetector(self.detector)
        self.display.register(self.gdetector, layer=0, clearable=False)
        self.is_display = True

    def process(self, event):
        particles = getattr(event, self.cfg_ana.particles)
        if self.is_display:
            self.display.clear()
            self.display.register(GTrajectories(particles), layer=1)
