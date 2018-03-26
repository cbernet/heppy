from heppy.framework.analyzer import Analyzer

class EventSkipper(Analyzer):
    
    def process(self, event):
        if event.iEv < self.cfg_ana.first_event:
            return False
        else:
            return True
        
