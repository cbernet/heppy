from heppy.framework.analyzer import Analyzer
from heppy.papas.data.eventplotter import EventPlotter

class PapasEventPlotter(Analyzer):
    '''Produces Standard Papas Event plots for a papasevent including simulation and reconstruction
    with option to plot subgroups of an event (linked objects from history)

    Example::
       
        from heppy.analyzers.PapasEventPlotter import PapasEventPlotter
        papas_plotter = cfg.Analyzer(
            PapasEventPlotter,
            detector = CMS,
            projections = ['xy', 'yz'],
            plottype = "event",
            to_file = False,
            num_subgroups = 2
        )

    @param detector: detector model used for the simulation
    @param projections: a list of required projections, eg.
       ['xy', 'yz', 'xz' ,'ECAL_thetaphi', 'HCAL_thetaphi']
    @param plottype: "event" or "subgroups"
    @param to_file: save display to png file? 
    @param num_subgroups: if set, display the num_subgroups largest
       subgroups. Otherwise display everything.
    '''

    def __init__(self, *args, **kwargs):
        super(PapasEventPlotter, self).__init__(*args, **kwargs)  

    def process(self, event):
        '''process event.
        
         The event must contain:
          - papasevent: event structure containing all the information from papas
        '''
        
        if self.cfg_ana.display:
            self.eventplot = EventPlotter(event.papasevent,
                                          self.cfg_ana.detector,
                                          self.cfg_ana.projections,
                                          self.dirName)
            if self.cfg_ana.plottype == "event":
                self.eventplot.plot_event_compare(self.cfg_ana.to_file)
            elif self.cfg_ana.plottype == "subgroups":
                num_subgroups = None
                if hasattr(self.cfg_ana, "num_subgroups"):
                    num_subgroups = self.cfg_ana.num_subgroups            
                self.eventplot.plot_event_subgroups_compare(self.cfg_ana.to_file,
                                                            num_subgroups)
        self.cfg_ana.display = False #only do display for first event in a loop
