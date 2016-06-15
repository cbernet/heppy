#todo remove pfevent from this class once we have written a helper class to print the block and its elements
from DAG import Node, DAGFloodFill

#temp
from heppy.papas.cpp.physicsoutput import PhysicsOutput as  pdebug
from heppy.papas.data.identifier import Identifier
import collections

#todo remove pfevent from this class once we have written a helper class to print the block and its elements


class GraphBuilder(object):
    ''' GraphBuilder takes a set of identifiers and a dict of associated edges which have distance and link info
        It uses the distances between elements to construct a set of subgraphs
        Each element will end up in one (and only one) subgraph
        

        attributes:

        ids   : list of unique identifiers eg of tracks, clusters etc
        edges : dict of edges which contains all edges between the ids (and maybe more)
                an edge records the distance between two ids
        nodes : a set of nodes corresponding to the unique ids which is used to construct a graph
                and thus find distinct blocks
        subgraphs : a list of subgraphs, each subgraph is a list of connected ids

        Usage example:
            graph = GraphBuilder(ids, edges)
            
    '''
    def __init__(self, ids, edges):
        '''
        ids   : list of unique identifiers eg of tracks, clusters etc
        edges : dict of edges which contains all edges between the ids (and maybe more)
                an edge records the distance/link between two ids
        '''
        self.ids = ids
        self.edges = edges
        
        ids.sort()
        
        #for idt in ids:
        #    pdebug.write(str('Node {:9}\n').format(Identifier.pretty(idt)))

        # build the block nodes (separate graph which will use distances between items to determine links)
        
        nodes = dict((idt, Node(idt)) for idt in ids)
        self.nodes = collections.OrderedDict( sorted(nodes.items(), key=lambda t: t[0]) )  #needed to match with cpp

        for edge in edges.itervalues():
            #add linkage info into the nodes dictionary
            if  edge.linked: #this is actually an undirected link - OK for undirected searches 
                self.nodes[edge.id1].add_child(self.nodes[edge.id2]) 
                #pdebug.write(str('      Add Child {:9} to  Node {:9}\n').format(Identifier.pretty(edge.id2),Identifier.pretty(edge.id1)))
                
        #for node in self.nodes.itervalues():
            #pdebug.write(str('Node {:9}\n').format(Identifier.pretty(node.get_value())))
            #for c in node.children:
                #pdebug.write(str('      Children Node {:9}\n').format(Identifier.pretty(c.get_value())))
            #for p in node.parents:
                #pdebug.write(str('      Parent Node {:9}\n').format(Identifier.pretty(p.get_value())))
            
        
        # build the subgraphs of connected nodes
        self.subgraphs = []
        for subgraphlist in DAGFloodFill(self.nodes).blocks: # change to subgraphs
            element_ids = [] 
            #pdebug.write("Group\n")
            # NB the nodes that are found by FloodFill are the Nodes describing links between items
            # we want the ids of these nodes
            for node in subgraphlist:
                #pdebug.write(str('inside Node {:9}\n').format(Identifier.pretty(node.get_value())))
                element_ids.append(node.get_value())        
            self.subgraphs.append(sorted(element_ids))


    def __str__(self):
        descrip = "{ "
        
        for subgraph in  self.subgraphs:
            descrip =  descrip +  " ("
            for elemid in  subgraph:
                descrip = descrip + str(elem) +  " "
            descrip =  descrip +  " )"    
        descrip = descrip + "}\n"
        return descrip  

    def __repr__(self):
        return self.__str__()     