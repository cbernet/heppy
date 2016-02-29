from heppy.framework.analyzer import Analyzer

import copy
import random

class LeptonSmearer(Analyzer):
    
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
        '''just a simple smearing, could implement a detailed model here.'''
        smeared = self.smear(obj, 1, 0.1)
        if abs(smeared.eta())<2.5 and smeared.e()>5:
            return smeared
        else:
            return None

        
    def smear_muon(self, obj):
        '''just a simple smearing, could implement a detailed model here.'''
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
