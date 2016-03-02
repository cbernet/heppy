from heppy.framework.analyzer import Analyzer

import copy
import random

class LeptonSmearer(Analyzer):
    '''Apply a simple resolution and efficiency model to electrons and muons.
    
    This module is just an example, you may write your own if you want a different 
    energy and resolution model.

    Example:

    from heppy.analyzers.examples.zh.LeptonSmearer import LeptonSmearer
    leptons = cfg.Analyzer(
    LeptonSmearer,
      'leptons',
      output = 'leptons',
      input_objects = 'leptons_true',
    )
    
    * input_objects: input particle collection 

    * output: output particle collection. 

    electrons and muons are smeared.
    Then, if they are in the detector and if their energy is high enough, 
    they are copied to the output collection. 

    Other particles in the input_objects collection are untouched and always copied 
    to the output. 
    '''
    
    def process(self, event):
        input_objects = getattr(event, self.cfg_ana.input_objects)
        output = []
        for obj in input_objects:
            smeared = obj
            if abs(obj.pdgid() == 11):
                smeared = self.smear_electron(obj)
            elif abs(obj.pdgid() == 13):
                smeared = self.smear_muon(obj)
            if smeared: 
                output.append(smeared) 
        setattr(event, self.cfg_ana.output, output)

    def smear_electron(self, obj):
        '''just a simple smearing, could implement a detailed model here.
        
        Gaussian smearing of the p4 by 10%.
        Electron accepted if smeared energy>5. and |eta|<2.5
        '''
        smeared = self.smear(obj, 1, 0.1)
        if abs(smeared.eta())<2.5 and smeared.e()>5:
            return smeared
        else:
            return None

        
    def smear_muon(self, obj):
        '''just a simple smearing, could implement a detailed model here.

        Gaussian smearing of the p4 by 5%.
        Electron accepted if smeared energy>5. and |eta|<2
        '''
        smeared = self.smear(obj, 1, 0.05)
        if abs(smeared.eta())<2. and smeared.e()>5:
            return smeared
        else:
            return None


    def smear(self, obj, mu, sigma):
        smear_factor = random.gauss(mu, sigma) 
        smeared = copy.deepcopy(obj)
        smeared._tlv *= smear_factor
        return smeared
