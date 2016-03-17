
import itertools
from DAG import Node, DAGFloodFill
from edge import Edge
from heppy.papas.aliceproto.identifier import Identifier


class PFBlock(object):
    ''' A Particle Flow Block stores a set of element ids that are connected to each other
     together with the edge data (distances) for each possible edge combination
     
     attributes: 
     
     uniqueid : this blocks unique id generated from Identifier class
     element_uniqueids : list of uniqueids of its elements
     pfevent : contains the tracks and clusters and a get_object method to allow access to the
               underlying objects given their uniqueid
     edges : Dictionary of all the edge cominations in the block dict{edgekey : Edge} 
             use  get_edge(id1,id2) to find an edge
     is_active : bool true/false, set to false if the block is subdivided
     
     Usage:
            block = PFBlock(element_ids,  edges, get_object) 
            for uid in block.element_uniqueids:
                 print self.get_object(uid)).__str__() + "\n"
            
     '''
    def __init__(self, element_ids, edges, pfevent): 
        ''' 
            element_ids:  list of the uniqueids of the elements to go in this block [id1,id2,...]
            edges: is a dictionary of edges it must contain at least all needed edges
            pfevent: allows access to the underlying elements given a uniqueid (via get_object)
        '''
        #make a uniqueid for this block
        self.uniqueid = Identifier.make_id(self,Identifier.PFOBJECTTYPE.BLOCK) 
        self.is_active = True
        
        #allow access to the underlying objects
        self.pfevent=pfevent        
        
        #order the elements by element type (ecal, hcal, track) and then by element id  
        #eg E1 E2 H3
        self.element_uniqueids =sorted(element_ids, key =lambda  x: Identifier.type_short_code(x) + str(x) )
        
        #extract the relevant parts of the complete set of edges and store this within the block
        self.edges = dict()       
        for id1, id2 in itertools.combinations(self.element_uniqueids,2):
            key = Edge.make_key(id1,id2)
            self.edges[key] = edges[key]
        print("finished block")    
   
    def count_ecal(self):
        ''' Counts how many ecal cluster ids are in the block '''
        count=0
        for elem in self.element_uniqueids:
            count += Identifier.is_ecal(elem)
        return count
    
    def count_tracks(self):
        ''' Counts how many track ids are in the block '''
        count = 0
        for elem in self.element_uniqueids:
            count += Identifier.is_track(elem)
        return count    
        
    def count_hcal(self):
        ''' Counts how many hcal cluster ids are in the block '''
        count = 0
        for elem in self.element_uniqueids:
            count += Identifier.is_hcal(elem)
        return count  
    
    def __len__(self) :
        return len(self.element_uniqueids)   
    
    def linked_edges(self,uniqueid,edgetype=None) :
        ''' Returns list of all linked edges of a given edge type that are connected to a given id - sorted in order of increasing distance'''
        linked_edges=[]
        for edge in self.edges.itervalues():
            if edge.linked and (edge.id1==uniqueid or edge.id2==uniqueid ) :
                if (edgetype != None) and (edge.edgetype() == edgetype ):
                    linked_edges.append(edge)
                elif edgetype == None :
                    linked_edges.append(edge)
        linked_edges.sort( key = lambda x: x.distance)
        return linked_edges
                   
    def linked_ids(self,uniqueid,edgetype=None) :
            ''' Returns list of all linked ids of a given edge type that are connected to a given id - sorted in order of increasing distance'''
            linked_ids=[]  
            linked_edges=[]
            linked_edges=self.linked_edges(uniqueid,edgetype)
            if len(linked_edges) :
                for edge in linked_edges:
                    if edge.id1==uniqueid :
                        linked_ids.append(edge.id2)
                    else :
                        linked_ids.append(edge.id1)
            return linked_ids
    
    def elements_string(self) : 
        ''' Construct a string descrip of each of the elements in a block '''
        count = 0
        elemdetails = "\n      elements: {\n"  
        for uid in self.element_uniqueids:
            elemname = Identifier.type_short_code(uid) +str(count) + ":" + str(uid)  + ": "
            elemdetails += "      " + elemname + ":"  + self.pfevent.get_object(uid).__str__() + "\n"
            count = count + 1            
        return elemdetails + "      }"
    
    def edge_matrix_string(self) :
        ''' produces a string containing the the lower part of the matrix of distances between elements
        elements are ordered as ECAL(E), HCAL(H), Track(T) and by edgekey '''
    
        # make the header line for the matrix       
        count = 0
        matrixstr = "      distances:\n           "
        for e1 in self.element_uniqueids :
            # will produce short id of form E2 H3, T4 etc in tidy format
            elemstr = Identifier.type_short_code(e1) + str(count)
            matrixstr +=  "{:>9}".format(elemstr)
            count += 1
        matrixstr +=  "\n"
    
        #for each element find distances to all other items that are in the lower part of the matrix
        countrow = 0
        for e1 in self.element_uniqueids : # this will be the rows
            countcol = 0
            rowstr = ""
            #make short name for the row element eg E3, H5 etc
            rowname = Identifier.type_short_code(e1) +str(countrow)
            for e2 in sorted(self.element_uniqueids) :  # these will be the columns
                #make short name for the col element eg E3, H5                
                colname = Identifier.type_short_code(e1) + str(countcol) 
                countcol += 1
                if (e1 == e2) :
                    rowstr += "       . "
                    break
                rowstr   += "{:8.4f}".format(self.get_edge(e1,e2).distance) + " "
            matrixstr += "{:>11}".format(rowname) + rowstr + "\n"
            countrow += 1        
    
        return matrixstr   +"      }\n"
    
    def get_edge(self,id1, id2) :
        ''' Find the edge corresponding to e1 e2 
            Note that make_key deals with whether it is get_edge(e1, e2) or get_edge(e2, e1) (either order gives same result)
            '''
        return self.edges[Edge.make_key(id1,id2)]
    
    def __str__(self):
        ''' Block description which includes list of elements and a matrix of distances  '''
        descrip = str('\nid={blockid}: ecals = {count_ecal} hcals = {count_hcal} tracks = {count_tracks}'.format(
            blockid      = self.uniqueid,
            count_ecal   = self.count_ecal(),
            count_hcal   = self.count_hcal(),
            count_tracks = self.count_tracks() )
        ) 
        descrip += self.elements_string()        
        descrip += "\n" + self.edge_matrix_string()     
        return descrip
    
    def __repr__(self):
            return self.__str__()    

        
class BlockBuilder(object):
    ''' BlockBuilder takes a set of identifiers and a dict of associated edges which have distance and link info
        It uses the distances between elements to construct a set of blocks
        Each element will end up in one (and only one block)
        Blocks retain information of the elements and the distances between elements
        The blocks can then be used for future particle reconstruction
        The ids must be unique and are expected to come from the Identifier class
        
        attributes:
        
        ids   : list of unique identifiers eg of tracks, clusters etc
        edges : dict of edges which contains all edges between the ids (and maybe more)
                an edge records the distance between two ids
        history_nodes : dictionary of nodes that describe which elements are parents of which blocks 
                        if a history_nodes tree is passed in then 
                        the additional history will be added into the exisiting history 
        pfevent : the particle flow event object which is needed so that the underlying object can 
                be retrieved
        nodes : a set of nodes corresponding to the unique ids which is used to construct a graph
                and thus find distinct blocks
        blocks: the resulting blocks
    
        
        Usage example:

            builder = BlockBuilder(ids, edges, history_nodes, pfevent)
            for b in builder.blocks.itervalues() :
                print b
    '''
    def __init__(self, ids, edges, history_nodes = None, pfevent = None):
        '''
        ids   : list of unique identifiers eg of tracks, clusters etc
        edges : dict of edges which contains all edges between the ids (and maybe more)
                an edge records the distance/link between two ids
        history_nodes : optional dictionary of nodes that describe which elements are parents of which blocks 
                        if a history_nodes tree is passed in then 
                        the additional history will be added into the exisiting history 
        pfevent : particle flow event object  needed so that the underlying object can 
                be retrieved
       
        '''
        
        #given a unique id this can return the underying object
        self.pfevent = pfevent
        
        self.edges = edges
        self.history_nodes = history_nodes
        
        # build the block nodes (separate graph which will use distances between items to determine links)
        self.nodes = dict( (idt, Node(idt)) for idt in ids ) 
        
        for edge in edges.itervalues() :
            #add linkage info into the nodes dictionary
            if  edge.linked: #this is actually an undirected link - OK for undirected searches 
                self.nodes[edge.id1].add_child(self.nodes[edge.id2])            

        # build the blocks of connected nodes
        self.blocks = dict()
        self._make_blocks()        
        
        
    
        
    def _make_blocks (self) :
        ''' uses the DAGfloodfill algorithm in connection with the BlockBuilder nodes
            to work out which elements are connected
            Each set of connected elements will be used to make a new PFBlock
        ''' 
        for blocknodelist in DAGFloodFill(self.nodes).blocks :
            element_ids = [] 
            # NB the nodes that are found by FloodFill are the Nodes describing links between items
            # we want the ids of these nodes
            for node in blocknodelist :
                element_ids.append(node.get_value())
    
            #now we can make the block
            block = PFBlock(element_ids,  self.edges, self.pfevent)        
           
            #put the block in the dict of blocks            
            self.blocks[block.uniqueid] = block        
            
            #make a node for the block and add into the history Nodes
            if (self.history_nodes != None) :
                blocknode = Node(block.uniqueid)
                self.history_nodes[block.uniqueid] = blocknode
                #now add in the links between the block elements and the block into the history_nodes
                for elemid in block.element_uniqueids :
                    self.history_nodes[elemid].add_child(blocknode)            
        
                
    def __str__(self):
        descrip = "{ "
        for block in self.blocks.iteritems() :
            descrip = descrip + block.__str__()
        descrip = descrip + "}\n"
        return descrip  
    
    def __repr__(self):
        return self.__str__()     