from heppy.framework.analyzer import Analyzer
from heppy.papas.pfalgo.historyplotter import HistoryPlotter

class PapasDAGPlotter(Analyzer):
    '''Produces DAG plots for papasevent 

        Example: 
        from heppy.analyzers.PapasDAGPlotter import PapasDAGPlotter
        papas_plotter = cfg.Analyzer(
            PapasDAGPlotter,
            plottype = "dag_event"
            show_file = False
        )

     * plot_type : "dag_event" or "dag_subgroups"
     
     * show_file: whether to open the dag event output file after producing it (this option not used for subgroups)
     
     * num_subgroups: optional  for "dag_subgroups" says how many subgroups to produce plots for
                      if not specified all subgroups are produced
 
    '''

    def __init__(self, *args, **kwargs):
        super(PapasDAGPlotter, self).__init__(*args, **kwargs)  
        self.show_file = self.cfg_ana.show_file
        self.plottype = self.cfg_ana.plottype
        self.num_subgroups = None
        if hasattr(self.cfg_ana, "num_subgroups"):
            self.num_subgroups = self.cfg_ana.num_subgroups

    def process(self, event):
        '''
         The event must contain a papasevent.
        '''
        self.histplot = HistoryPlotter(event.papasevent, event.detector)
        
        if self.plottype == "dag_event":
            self.histplot.plot_dag_event(self.show_file) 
        elif self.plottype == "dag_subgroups":
            self.histplot.plot_dag_subgroups(self.num_subgroups)
   