from heppy.framework.analyzer import Analyzer
from heppy.papas.data.eventplotter import EventPlotter

class PapasEventPlotter(Analyzer):
    '''Produces Standard Papas Event plots for a papasevent including simulation and reconstruction
    with option to plot subgroups of an event (linked objects from history)

    Example::
       
        from heppy.analyzers.PapasEventPlotter import PapasEventPlotter
        papas_event_plot = cfg.Analyzer(
            PapasEventPlotter,
            projections = ['xy', 'yz'],
            screennames = ["simulated", "reconstructed"],
            particles_type_and_subtypes = ['ps', 'pr'],
            clusters_type_and_subtypes = [['es', 'hs'],['em', 'hm']], 
            detector = detector,
            plottype = "event",
            to_file = True,
            display = True
        )


    @param projections: a list of required projections, eg.
       ['xy', 'yz', 'xz' ,'ECAL_thetaphi', 'HCAL_thetaphi']
    @param screennames: List of names for subscreens (also used to decide whether to plot a single event display 
                    or a comparison (two plots side by side)) eg ["simulation", "reconstruction"]
    @param particles_type_and_subtypes: list of particle type_and_subtypes to plot. Length of list must match the length of screennames
                                 eg ['ps', 'pr'] for simulated particles ('ps') on left, reconstructed particles ('pr') on right
    @param clusters_type_and_subtypes: list of lists of  clusters to plot, length of list must be same as the length of screennames
                    eg [['es', 'hs'], ['em', 'hm']] would plot smeared ecals ('es') and smeared hcals ('hs') on left
                        and merged ecals ('em') and merged hcals ('hm') on right
    @param detector: detector model used for the simulation
    @param plottype: "event" or "subgroups"
    @param to_file: save display to png file
    @param num_subgroups: if set, display the num_subgroups largest
    @param display: if false nothing will be produced
       subgroups. Otherwise display everything.
    '''

    def __init__(self, *args, **kwargs):
        super(PapasEventPlotter, self).__init__(*args, **kwargs)  

    def process(self, event):
        '''process event.
        
         The event must contain:
          - papasevent: event structure containing all the information from papas
        '''
        if  hasattr(self.cfg_ana, 'display') and self.cfg_ana.display:
            self.eventplot = EventPlotter(event.papasevent,
                                          self.cfg_ana.detector,
                                          self.cfg_ana.projections,
                                          self.dirName)
            num_subgroups = None
            if hasattr(self.cfg_ana, "num_subgroups"):
                num_subgroups = self.cfg_ana.num_subgroups              
            self.eventplot.plot(self.cfg_ana.plottype, 
                                    self.cfg_ana.screennames, 
                                    self.cfg_ana.particles_type_and_subtypes,
                                    self.cfg_ana.clusters_type_and_subtypes,
                                    num_subgroups, 
                                    to_file=self.cfg_ana.to_file)
            
        self.cfg_ana.display = False #only do display for first event in a loop
