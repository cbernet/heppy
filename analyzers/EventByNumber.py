from heppy.framework.analyzer import Analyzer

class EventByNumber(Analyzer):
    
    def process(self, event):
        if event.iEv not in self.cfg_ana.event_numbers:
            return False
        else:
            return True
