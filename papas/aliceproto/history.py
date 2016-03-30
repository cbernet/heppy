from heppy.papas.aliceproto.DAG import Node, BreadthFirstSearch
from heppy.papas.aliceproto.identifier import Identifier

class History(object):
    '''   
       Object to assist with printing and reconstructing histories
       only just started ...
    '''    
    def __init__(self, history_nodes,pfevent):
        self.history_nodes = history_nodes
        self.pfevent = pfevent
        
    def summary_of_links(self, id):
    
        BFS = BreadthFirstSearch(self.history_nodes[id],"undirected")
        print "history connected to node:", id
        
        track_descrips = []
        ecal_descrips = []
        hcal_descrips = []
        #sim_particle_descrips = []
        rec_particle_descrips = []
        block_descrips = []
        for n in BFS.result :
            z = n.get_value()
            descrip = self.pfevent.get_object(z).__str__()
           # if (Identifier.is_particle(z)):
            #    sim_particle_descrips.append(descrip)
            if (Identifier.is_block(z)):
                block_descrips.append(descrip)            
            if (Identifier.is_track(z)):
                track_descrips.append(descrip)         
            if (Identifier.is_ecal(z)):
                ecal_descrips.append(descrip)  
            if (Identifier.is_hcal(z)):
                hcal_descrips.append(descrip)         
            if (Identifier.is_rec_particle(z)):
                rec_particle_descrips.append(descrip)               
        
        print "block", block_descrips
        print "       tracks", track_descrips
        print "        ecals", ecal_descrips
        print "        hcals", hcal_descrips
        print "rec particles", rec_particle_descrips
        
        #print "reconstructed particles"