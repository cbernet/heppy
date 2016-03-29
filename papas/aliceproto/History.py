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
        
        tracks = []
        ecals = []
        hcals = []
        sim_particles = []
        rec_particles = []
        for n in BFS.result :
            z = n.get_value()
            descrip = self.pfevent.get_object(z).__str__()
            if (Identifier.is_particle(z)):
                sim_particles.append(descrip)
            if (Identifier.is_track(z)):
                tracks.append(descrip)         
            if (Identifier.is_ecal(z)):
                ecals.append(descrip)  
            if (Identifier.is_hcal(z)):
                hcals.append(descrip)         
            if (Identifier.is_rec_particle(z)):
                rec_particles.append(descrip)               
        
        print "sim particles", sim_particles
        print "       tracks", tracks
        print "        ecals", ecals
        print "        hcals", hcals
        print "rec particles", rec_particles
        
        #print "reconstructed particles"