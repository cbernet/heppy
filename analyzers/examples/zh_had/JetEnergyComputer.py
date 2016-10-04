from heppy.framework.analyzer import Analyzer
import copy

class JetEnergyComputer(Analyzer):
    
    def process(self, event):
        sqrts = self.cfg_ana.sqrts
        jets = getattr(event, self.cfg_ana.input_jets)
        assert(len(jets) == 4)
        # here solve the equation to get the energy scale factor for each jet.
        scale_factors = [1] * 4
        output = []
        for jet, factor in zip(jets, scale_factors):
            # the jets should not be deepcopied
            # as they are heavy objects containing
            # in particular a list of consistuent particles 
            scaled_jet = copy.copy(jet)
            scaled_jet._tlv = copy.deepcopy(jet._tlv)
            scaled_jet._tlv *= factor
            output.append(scaled_jet)
        setattr(event, self.cfg_ana.output_jets, output)
