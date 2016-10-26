from heppy.framework.analyzer import Analyzer
from heppy.papas.data.eventplotter import EventPlotter

class PapasEventPlotter(Analyzer):
    '''Produces Standard Papas Event plots for a papasevent including simulation and reconstruction
       with option to plot subgroups of an event (linked objects from history)

        Example:
        from heppy.analyzers.PapasEventPlotter import PapasEventPlotter
        papas_plotter = cfg.Analyzer(
            PapasEventPlotter,
            projections = ['xy', 'yz'],
            plottype = "event",
            to_file = False,
            num_subgroups = 2
        )

        * projections a list of required projections eg ['xy', 'yz', 'xz' ,'ECAL_thetaphi',
                           'HCAL_thetaphi'
        * plottype = "event" or "subgroups"
        * to_file = True/False - whether to send output to file
        * num_subgroups = integer (optional) produce outputs for the largest n subgroups, if unset will produce everything

    '''

    def __init__(self, *args, **kwargs):
        super(PapasEventPlotter, self).__init__(*args, **kwargs)  

    def process(self, event):
        '''
         The event must contain a papasevent.
        '''
        self.eventplot = EventPlotter(event.papasevent, event.detector, self.cfg_ana.projections, self.cfg_ana.dirName)
        if self.cfg_ana.plottype == "event":
            self.eventplot.plot_event_compare(self.cfg_ana.to_file)
        elif self.cfg_ana.plottype == "subgroups":
            num_subgroups = None
            if hasattr(self.cfg_ana, "num_subgroups"):
                num_subgroups = self.cfg_ana.num_subgroups            
            self.eventplot.plot_event_subgroups_compare(self.cfg_ana.to_file, num_subgroups)
