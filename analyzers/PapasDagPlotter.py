from heppy.framework.analyzer import Analyzer
from heppy.papas.graphtools.historyplotter import HistoryPlotter

class PapasDAGPlotter(Analyzer):
    '''Produces a graphical plot of a Directed Acyclic Graph (DAG) for papasevents based on pydot/graphviz
       This can be used to plot the relationships between particles/clusters/tracks for simulation
       and reconstruction
       eg: gives a much prettier graphical representation of something like the following
    
             Particle  - Cluster  -> SmearedCluster  - Reconstructed Particle
                       \ Track    -> Smeared Track    /
                        

        Example: 
        #produce a plot of all elements in the papasevent
        from heppy.analyzers.PapasDAGPlotter import PapasDAGPlotter
        papas_plotter = cfg.Analyzer(
            PapasDAGPlotter,
            plottype = "dag_event"
            show_file = False
        )
        
        #produce individual plots of the 4 (a configurable parameter) biggest connected subgroups in the event
        # a subgroup is a set of linked objects eg everything linked (directly or indirectly) to specific  particle
        # would be a subgroup
        from heppy.analyzers.PapasDagPlotter import PapasDAGPlotter
        papas_dag_subgroups= cfg.Analyzer( 
            PapasDAGPlotter,
            plottype = "dag_subgroups",
            show_file = False,
            num_subgroups = 4
        )

     * plot_type : "dag_event" or "dag_subgroups"
                    dag_event will plot everything in the papasevent
                    dag_subgroups will produce separate plots for subgroups of linked items in the papasevent (this can be limited
                    to the largest subgroups using the num_subgroups option below) 
     
     * show_file: whether to open the dag event output file after producing it (this option not used for subgroups)
     
     * num_subgroups: optional  for "dag_subgroups" says how many subgroups to produce plots for
                      if not specified all subgroups are produced. If not specified all subgroups will be plotted.
                      Beware as this may be a very large number of plots!
 
 
    TODO: consider better ways to select "interestign subgroups"
        apply some safety mechanisms to limit number of plots or to stop producing plots if in 
    '''

    def __init__(self, *args, **kwargs):
        super(PapasDAGPlotter, self).__init__(*args, **kwargs)  

    def process(self, event):
        '''
         The event must contain a papasevent.
        '''
        self.dirName = '/'.join( [self.looperName, self.name] )
                  
        self.histplot = HistoryPlotter(event.papasevent, self.dirName)
        if self.cfg_ana.plottype == "dag_event":
            self.histplot.plot_dag_event(self.cfg_ana.show_file) 
        elif self.cfg_ana.plottype == "dag_subgroups":
            num_subgroups = None
            if hasattr(self.cfg_ana, "num_subgroups"):
                num_subgroups = self.cfg_ana.num_subgroups            
            self.histplot.plot_dag_subgroups(num_subgroups)

