from heppy.papas.graphtools.DAG import Node, BreadthFirstSearchIterative
from heppy.papas.data.identifier import Identifier
import pydot

class History(object):
    '''   
       Object to assist with printing and reconstructing histories
       may need to be merged with pfevent
       only just started ...
    '''    
    def __init__(self, history_nodes, pfevent):
        #this information information needed to be able to unravel information based on a unique identifier
        self.history_nodes = history_nodes
        self.pfevent = pfevent
        self.graph = pydot.Dot(graph_type='digraph')
        
        
        self.graphnodes = dict()        
        self.graph.write_png('example2_graph.png')
        
    def summary_of_linked_elems(self, id, direction):
    
        #find everything that is linked to this id
        #and write a summary of what is found
        #the BFS search returns a list of the ids that are  connected to the id of interest
        BFS = BreadthFirstSearchIterative(self.history_nodes[id], direction)
       
        self.print_linked_ids(BFS.result)
        self.print_short_summary(id, BFS.result)
        self.graph_graph(id, BFS.result)
    
    def object(self, node):
        z = node.get_value()
        return self.pfevent.get_object(z)        
        
    def short_name(self, node):
        z = node.get_value()
        return Identifier.pretty(z)
    
    def short(self, node):
            z = node.get_value()
            return Identifier.type_short_code(z) 
        
    def short_info(self, node):
        return self.object(node).shortinfo()       
       
    def colour(self, node):
        cols =["red", "lightblue", "green", "yellow","cyan", "grey", "white","pink"]
        return cols[Identifier.get_type(node.get_value())]            
            
       
       

    def object(self, node):
        z = node.get_value()
        return self.pfevent.get_object(z) 
    
    def print_linked_ids(self,   nodeids): 
        idvec={}    
        tracks = []
        ecals = []
        hcals = []
        sim_particles = []
        
        smeared_ecals = []
        smeared_hcals = []
        gen_particles = []
        gen_tracks = []
        gen_ecals = []
        gen_hcals = []
                        
        rec_particles = []
        blocks = []        
        for n in nodeids:       
            z = n.get_value()
            obj = self.pfevent.get_object(z)
            if (Identifier.is_block(z)):
                blocks.append(obj)            
            elif (Identifier.is_track(z)):
                if type(obj).__name__ == "Track":
                    gen_tracks.append(obj)  
                if type(obj).__name__ == "SmearedTrack":
                    tracks.append(obj)                  
            elif (Identifier.is_ecal(z)):
                if type(obj).__name__ == "Cluster":
                    gen_ecals.append(obj)  
                elif type(obj).__name__ == "SmearedCluster":
                    smeared_ecals.append(obj)  
                else:
                    ecals.append(obj)  
            elif (Identifier.is_hcal(z)):
                if type(obj).__name__ == "Cluster":
                    gen_hcals.append(obj)  
                elif type(obj).__name__ == "SmearedCluster":
                    smeared_hcals.append(obj)   
                else:
                    hcals.append(obj)         
            elif (Identifier.is_rec_particle(z)):
                rec_particles.append(obj) 
            elif (Identifier.is_particle(z)):
                gen_particles.append(obj) 
            elif (Identifier.is_sim_particle(z)):
                sim_particles.append(obj)          
       
        idvec["blocks"]=blocks
        idvec["tracks"]=tracks
        idvec["ecals"]=ecals
        idvec["hcals"]=hcals
        idvec["sim_particles"]=sim_particles
        
        idvec["smeared_ecals"]=smeared_ecals
        idvec["smeared_hcals"]=smeared_hcals
        idvec["gen_particles"]=gen_particles
        idvec["gen_tracks"]=gen_tracks
        idvec["gen_ecals"]=gen_ecals
        idvec["gen_hcals"]=gen_hcals
          
        idvec["rec_particles"]=rec_particles
        print idvec
        return idvec   
    
    def print_graph (self,  nodeids):
        nodestring =""
        
        for node in nodeids :
            nodestring += Identifier.pretty(node.get_value()) 
            for c in node.children :
                nodestring += Identifier.pretty(c.get_value()) 
   
    def graph_graph (self, id, nodeids):
       
        
        # this time, in graph_type we specify we want a DIrected GRAPH
        alreadythere=False;
        
        
        for node in nodeids:
            if  self.graphnodes.has_key(self.short_name(node))==False:
                self.graphnodes[self.short_name(node)] = pydot.Node(self.short_name(node), style="filled", label=self.short_info(node), fillcolor=self.colour(node))
                self.graph.add_node( self.graphnodes[self.short_name(node)])
        for node in nodeids:
            for c in node.parents:
                if len(self.graph.get_edge(self.graphnodes[self.short_name(c)],self.graphnodes[self.short_name(node)]))==0:
                    self.graph.add_edge(pydot.Edge(  self.graphnodes[self.short_name(c)],self.graphnodes[self.short_name(node)]))
                    alreadythere=True
        if alreadythere==False:
            pass
            #for c in node.children:
            #    self.graph.add_edge(pydot.Edge(  self.graphnodes[self.short_name(c)],self.graphnodes[self.short_name(node)]))            
                  
        self.graph.write_png('example2_graph.png')
        # but, let's make this last edge special, yes?
        #graph.add_edge(pydot.Edge(node_d, node_a, label="and back we go again", labelfontcolor="#009933", fontsize="10.0", color="blue"))
        
        # and we are done
        
   
   
       
    def print_long_summary(self, id,  nodeids):
    
       
       
        #collate the string descriptions
        track_descrips = []
        ecal_descrips = []
        hcal_descrips = []
        sim_particle_descrips = []
        
        smeared_ecal_descrips = []
        smeared_hcal_descrips = []
        gen_particle_descrips = []
        gen_track_descrips = []
        gen_ecal_descrips = []
        gen_hcal_descrips = []
                        
        rec_particle_descrips = []
        block_descrips = []
        

        for n in nodeids:
            
            z = n.get_value()
            obj = self.pfevent.get_object(z)
            descrip = obj.__str__()
           # if (Identifier.is_particle(z)):
            #    sim_particle_descrips.append(descrip)
            if (Identifier.is_block(z)):
                block_descrips.append(descrip)            
            elif (Identifier.is_track(z)):
                if type(obj).__name__ == "Track":
                    gen_track_descrips.append(descrip) 
                if type(obj).__name__ == "SmearedTrack":
                    track_descrips.append(descrip)                 
            elif (Identifier.is_ecal(z)):
                if type(obj).__name__ == "Cluster":
                    gen_ecal_descrips.append(descrip) 
                elif type(obj).__name__ == "SmearedCluster":
                    smeared_ecal_descrips.append(descrip)  
                else:
                    ecal_descrips.append(descrip)  
            elif (Identifier.is_hcal(z)):
                if type(obj).__name__ == "Cluster":
                    gen_hcal_descrips.append(descrip) 
                elif type(obj).__name__ == "SmearedCluster":
                    smeared_hcal_descrips.append(descrip)  
                else:
                    hcal_descrips.append(descrip)        
            elif (Identifier.is_rec_particle(z)):
                rec_particle_descrips.append(descrip)
            elif (Identifier.is_particle(z)):
                gen_particle_descrips.append(descrip)
            elif (Identifier.is_sim_particle(z)):
                sim_particle_descrips.append(descrip)            
                
        print ""
        print "history connected to node:", id, Identifier.pretty(id)
        print "gen particles", '\n              '.join(gen_particle_descrips)
       # print "sim_particles", '\n              '.join(sim_particle_descrips)
        print "       tracks", '\n              '.join(track_descrips)
        print "smearedtracks", '\n              '.join(gen_track_descrips)
        print "        ecals", '\n              '.join(ecal_descrips)
        print "smeared ecals", '\n              '.join(smeared_ecal_descrips)
        print "    gen ecals", '\n              '.join(gen_ecal_descrips)
        print "        hcals", '\n              '.join(hcal_descrips)
        print "smeared hcals", '\n              '.join(smeared_hcal_descrips)
        print "    gen hcals", '\n              '.join(gen_hcal_descrips    )    
        print "rec particles", '\n              '.join(rec_particle_descrips)
        pass
    
    
    def print_short_summary(self, id,  nodeids):
    
       
       
        #collate the string descriptions
        track_descrips = []
        ecal_descrips = []
        hcal_descrips = []
        sim_particle_descrips = []
        
        smeared_ecal_descrips = []
        smeared_hcal_descrips = []
        gen_particle_descrips = []
        gen_track_descrips = []
        gen_ecal_descrips = []
        gen_hcal_descrips = []
                        
        rec_particle_descrips = []
        block_descrips = []
        

        for n in nodeids:
            
            z = n.get_value()
            obj = self.pfevent.get_object(z)
            descrip = Identifier.pretty(z) + ":" + obj.shortinfo()
           # if (Identifier.is_particle(z)):
            #    sim_particle_descrips.append(descrip)
            if (Identifier.is_block(z)):
                block_descrips.append(descrip)            
            elif (Identifier.is_track(z)):
                if type(obj).__name__ == "Track":
                    gen_track_descrips.append(descrip) 
                if type(obj).__name__ == "SmearedTrack":
                    track_descrips.append(descrip)                 
            elif (Identifier.is_ecal(z)):
                if type(obj).__name__ == "Cluster":
                    gen_ecal_descrips.append(descrip) 
                elif type(obj).__name__ == "SmearedCluster":
                    smeared_ecal_descrips.append(descrip)  
                else:
                    ecal_descrips.append(descrip)  
            elif (Identifier.is_hcal(z)):
                if type(obj).__name__ == "Cluster":
                    gen_hcal_descrips.append(descrip) 
                elif type(obj).__name__ == "SmearedCluster":
                    smeared_hcal_descrips.append(descrip)  
                else:
                    ecal_descrips.append(descrip)        
            elif (Identifier.is_rec_particle(z)):
                rec_particle_descrips.append(descrip)
            elif (Identifier.is_particle(z)):
                gen_particle_descrips.append(descrip)
            elif (Identifier.is_sim_particle(z)):
                sim_particle_descrips.append(descrip)            
                
        print ""
        print "history connected to node:", id, Identifier.pretty(id)
        print "gen particles", '\n              '.join(gen_particle_descrips)
       # print "sim_particles", '\n              '.join(sim_particle_descrips)
        print "       tracks", '\n              '.join(track_descrips)
        print "smearedtracks", '\n              '.join(gen_track_descrips)
        print "        ecals", '\n              '.join(ecal_descrips)
        print "smeared ecals", '\n              '.join(smeared_ecal_descrips)
        print "    gen ecals", '\n              '.join(gen_ecal_descrips)
        print "        hcals", '\n              '.join(hcal_descrips)
        print "smeared hcals", '\n              '.join(smeared_hcal_descrips)
        print "    gen hcals", '\n              '.join(gen_hcal_descrips    )    
        print "rec particles", '\n              '.join(rec_particle_descrips)
        pass
    