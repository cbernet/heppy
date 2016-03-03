from heppy.framework.analyzer import Analyzer

class Btagging(Analyzer):
    
    def process(self, event):
        jets = getattr(event, self.cfg_ana.input_objects)
        bjets = [jet for jet in jets if self.cfg_ana.filter_func(jet)]
        
        for jet in jets:
            jet.tags['b'] = self.cfg_ana.filter_func(jet)
        
        setattr(event, self.cfg_ana.output, bjets)
