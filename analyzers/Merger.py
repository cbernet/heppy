from heppy.framework.analyzer import Analyzer
import copy



class Merger(Analyzer):
        
    def process(self, event):
        inputA = getattr(event, self.cfg_ana.inputA)
        inputB = getattr(event, self.cfg_ana.inputB)
        
        #should this be a deep copy?
        output = copy.copy(inputA)
        output.extend(inputB)
        setattr( event, self.cfg_ana.output, output)
        
        
        
  