from heppy.framework.analyzer import Analyzer
import copy

class JetEnergyComputer(Analyzer):
    
    def process(self, event):
        jets = getattr(event, self.cfg_ana.input_jets)
        assert(len(jets) == 4)
        # here solve the equation to get the energy scale factor for each jet.
        scale_factors = [1] * 4
        output = []
        for jet, factor in zip(jets, scale_factors):
            scaled_jet = copy.deepcopy(jet)
            scaled_jet._tlv *= factor
            output.append(scaled_jet)
        setattr(event, self.cfg_ana.output_jets, output)
