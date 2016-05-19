from heppy.framework.analyzer import Analyzer
from ROOT import TVector3
#from heppy.framework.event import Event
from heppy.papas.path import Helix
#import collections

class ImpactParameter(Analyzer):

        
    def process(self, event):
        assumed_vertex = TVector3(0, 0, 0)
        jets = getattr(event, self.cfg_ana.jets)
        for jet in jets:
            #for ptc in jet.constituents[211]:
            #    IPsn = 1
            #    N_charge = 0
                #for i in range(len(const)):
                #    if const[i][1][0]._charge <> 0:
                #        if len const[i][1] > 0:
                #            for l in range(len(const[i][1]))
                #                partic = const[i][1][l]
                #                h = partic.path
                #                Helix.compute_IP(h, assumed_vertex)
                #                setattr(partic, self.IP, h.IP)
                #                setattr(partic, self.tIP, h.closest.t)
                #                setattr(partic, self.xIP, h.closest.x)
                #                setattr(partic, self.yIP, h.closest.y)
                #                setattr(partic, self.zIP, h.closest.z)
                #                IPsn *= h.IP
                #                N_charge += 1
                #        else :
                #            pass
                #    else :
                #        pass
                #if N_charge <> 0 :
                #    IPs = IPSn**(1.0/N_charge)
                #else :
                #    pass
            for id, ptcs in jet.constituents.iteritems():
                if id in [22,130]:
                    continue
                for ptc in ptcs :
                    if ptc._charge == 0 :
                        continue
                    ptc.path.compute_IP(assumed_vertex)
                    #jet.IP = ptc.path.IP
            #setattr(event, self.cfg_ana.output, IPs)
        
