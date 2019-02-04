from heppy.framework.analyzer import Analyzer

class ResonanceLegExtractor(Analyzer):
    
    def process(self, event):
        '''extract the legs of the first resonance 
        '''
        resonances = getattr(event, self.cfg_ana.resonances)
        legs = [] 
        if len(resonances):
            the_res = resonances[0]
            legs = [the_res.leg1(), the_res.leg2()]
        setattr(event,
                '_'.join([self.cfg_ana.resonances, 'legs']),
                legs)
        return True
