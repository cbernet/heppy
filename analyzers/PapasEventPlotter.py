from heppy.framework.analyzer import Analyzer
from heppy.papas.data.historyplotter import HistoryPlotter

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
        * to_file- whether to send output to file
        * num_subgroups - (optional) produce outputs for the largest n subgroups, if unset will produce everything

    '''

    def __init__(self, *args, **kwargs):
        super(PapasEventPlotter, self).__init__(*args, **kwargs)  
        self.to_file = self.cfg_ana.to_file
        self.projections = self.cfg_ana.projections
        self.plottype = self.cfg_ana.plottype
        self.num_subgroups = None
        if hasattr(self.cfg_ana, "num_subgroups"):
            self.num_subgroups = self.cfg_ana.num_subgroups

    def process(self, event):
        '''
         The event must contain a papasevent.
        '''
        self.histplot = HistoryPlotter(event.papasevent, event.detector, self.projections)
        if self.plottype == "event":
            self.histplot.plot_event_compare(self.to_file)
        elif self.plottype == "subgroups":
            self.histplot.plot_event_subgroups_compare(self.to_file, self.num_subgroups)
