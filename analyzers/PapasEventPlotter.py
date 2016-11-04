from heppy.framework.analyzer import Analyzer
from heppy.display.eventplotter import EventPlotter
from heppy.display.core import Display
from heppy.display.geometry import GDetector

class PapasEventPlotter(Analyzer):
    '''Produces Standard Papas Event plots for a papasevent including simulation and reconstruction
    with option to plot subgroups of an event (linked objects from history)

    Example::
       
        from heppy.analyzers.PapasEventPlotter import PapasEventPlotter
        papas_event_plot = cfg.Analyzer(
            PapasEventPlotter,
            detector = CMS,
            projections = ['xy', 'yz'],
            screennames = ["simulated", "reconstructed"],
            particles_type_and_subtypes = ['ps', 'pr'],
            clusters_type_and_subtypes = [['es', 'hs'],['em', 'hm']], 
            plottype = "event",
            save = True,
            display = True
        )

    @param detector: detector model used for the simulation
    @param projections: a list of required projections, eg.
       ['xy', 'yz', 'xz' ,'ECAL_thetaphi', 'HCAL_thetaphi']
    @param screennames: List of names for subscreens (also used to decide whether to plot a single event display 
                    or a comparison (two plots side by side)) eg ["simulation", "reconstruction"]
    @param particles_type_and_subtypes: list of particle type_and_subtypes to plot. Length of list must match the length of screennames
                                 eg ['ps', 'pr'] for simulated particles ('ps') on left, reconstructed particles ('pr') on right
    @param clusters_type_and_subtypes: list of lists of  clusters to plot, length of list must be same as the length of screennames
                    eg [['es', 'hs'], ['em', 'hm']] would plot smeared ecals ('es') and smeared hcals ('hs') on left
                        and merged ecals ('em') and merged hcals ('hm') on right
    @param plottype: "event" or "subgroups"
    @param save: save display to png file
    @param num_subgroups: if set, display the num_subgroups largest n subgroups. Otherwise display everything.
    @param display: if false nothing will be produced
      
    '''

    def __init__(self, *args, **kwargs):
        super(PapasEventPlotter, self).__init__(*args, **kwargs)  
    
    def __init_display(self):
        '''Sets up either a single or double paned Display
        '''
        self.display = Display(self.cfg_ana.projections, self.cfg_ana.screennames)
        self.display.register(GDetector(self.cfg_ana.detector), layer=0, clearable=False)     

    def process(self, event):
        '''process event.
        
         @param event: The event must contain a papasevnt: event structure containing all the information from papas
        '''
        if hasattr(self.cfg_ana, 'display') and self.cfg_ana.display:
            self.__init_display()
            eventplot = EventPlotter(event.papasevent, self.cfg_ana.detector, self.display, self.dirName)
            num_subgroups = None
            if hasattr(self.cfg_ana, "num_subgroups"):
                num_subgroups = self.cfg_ana.num_subgroups 
            eventplot.plot(self.cfg_ana.plottype, 
                           self.cfg_ana.particles_type_and_subtypes,
                           self.cfg_ana.clusters_type_and_subtypes,
                           num_subgroups, 
                           save=self.cfg_ana.save)
        self.cfg_ana.display = False #only do display for first event in a loop
