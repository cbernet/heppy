from heppy.framework.analyzer import Analyzer
from heppy.papas.data.historyhelper import HistoryHelper


class PapasHistoryPrinter(Analyzer):
    '''Produces experimental History outputs for a papasevent (prints text summary)
        
        Examples: 
        from heppy.analyzers.PapasHistoryPrinter import PapasHistoryPrinter
        papas_print_history_event = cfg.Analyzer(
            PapasHistoryPrinter,
            format = "event"
        )
        
        from heppy.analyzers.PapasHistoryPrinter import PapasHistoryPrinter
        papas_print_history = cfg.Analyzer(
            PapasHistoryPrinter,
            format = "subgroups",
            num_subgroups = 3 # biggest 3 subgroups will be printed
        )
        
        * format = "event" or "subgroups"
           "event" orders all elements in papasevent by id (which is in turn sorted 
                by object type, object subtype, object energy)
           "subgroups" the output will groups elements that are in a connected 
                subgroup (subgroup elements are sorted by id)
        
        * num_subgroups = optional, only used by subgroups format. If set, 
                prints biggest n subgroups otherwise all subgroups are printed
    '''

    def __init__(self, *args, **kwargs):
        super(PapasHistoryPrinter, self).__init__(*args, **kwargs)  
        
        self.format = self.cfg_ana.format
        self.num_subgroups = None #optional argument
        if hasattr(self.cfg_ana, "num_subgroups"):
            self.num_subgroups = self.cfg_ana.num_subgroups

    def process(self, event):
        '''
         The event must contain a papasevent.
        '''
        self.papasevent = event.papasevent
        self.hist = HistoryHelper(event.papasevent)
        if self.cfg_ana.format == "event":        
            print self.hist.summary_string_event()
        elif self.cfg_ana.format == "subgroups":
            num_subgroups = None
            if hasattr(self.cfg_ana, "num_subgroups"):
                num_subgroups = self.cfg_ana.num_subgroups            
            print self.hist.summary_string_subgroups(num_subgroups)
