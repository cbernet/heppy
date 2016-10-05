from heppy.framework.analyzer import Analyzer
from heppy.papas.data.historyhelper import HistoryHelper
from heppy.papas.data.historyplotter import HistoryPlotter

class PapasHistory(Analyzer):
    ''' Module to handle history? 
        
    '''

    def __init__(self, *args, **kwargs):
        super(PapasHistory, self).__init__(*args, **kwargs)  
        self.detector = self.cfg_ana.detector
        
        #TODO self.is_display = self.cfg_ana.display
        self.is_display = self.cfg_ana.is_display
        self.is_printout = self.cfg_ana.is_printout
        self.dag = self.cfg_ana.dag
        self.top = self.cfg_ana.top

    def process(self, event):
        ''' Produces experimental History outputs for the event (plots or text)'''
        
        #experimental for the time being
        self.papasevent = event.papasevent
        self.event = event
        self.hist = HistoryHelper(event.papasevent)
        self.histplot = HistoryPlotter(event.papasevent, self.detector, self.is_display)
        
        if self.is_printout:                               
            print self.hist.summary_string_event()
            print self.hist.summary_string_subgroups(top=self.top)

        #self.examples()
        if self.is_display:
            self.histplot.plot_event_compare()
            if self.dag:
                self.histplot.plot_dag_event(show=self.is_display)        
                self.histplot.plot_dag_subgroups(top=self.top , show=self.is_display) 

        #self.plot_subevents_compare()

    