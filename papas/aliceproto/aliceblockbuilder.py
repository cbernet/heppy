import itertools

from DAG import Node, BreadthFirstSearchIterative, DAGFloodFill
from heppy.papas.aliceproto.Identifier import Identifier
    
      
class Edge(object): 
    '''An Edge stores end node ids, distance between the nodes, and whether they are linked
       
       attributes:
       
       id1 : element1 uniqueid 
       id2 : element2 uniqueid
       key : unique key value created from id1 and id2 (order of id1 and id2 is not important) 
       distance: distance between two elements
       is_linked : boolean T/F
       link_type : not used right now
    '''
    ruler = None
    
    def __init__(self, id1, id2,  link_type, is_linked, distance): 
        ''' The Edge knows the ids of its ends, the distance between the two ends and whether or not they are linked '''
        self.id1 = id1
        self.id2 = id2
        self.distance = distance
        self.link_type = link_type
        self.linked = is_linked
        self.key = Edge.make_key(id1,id2) 

    def __str__(self):
        descrip = str(self.link_type) + "=" + str(self.distance)+  " (" + str( self.linked) + " ) :" + self.descrip
        return descrip
    
    def __repr__(self):
        return self.__str__()      
    
    @staticmethod 
    def make_key(id1,id2):
        '''method to create a key based on two ids that can then be used to retrieve a specific edge
        ''' 
        return hash(tuple(sorted([id1,id2])))

  
class PFBlock(object):
    ''' A Particle Flow Block stores a set of element ids that are connected to each other
     together with the edge data (distances) for each possible edge combination
     
     attributes: 
     
     uniqueid : this blocks unique id
     element_uniqueids : list of uniqueids of its elements
     edges : Dictionary of all the edge cominations in the block dict{edgekey : Edge} 
             use  get_edge(id1,id2) to find an edge
     get_object : get_object(id1) returns the underlying object with this id
     
     Usage:
            block = PFBlock(element_ids,  edges, get_object) 
            for uid in block.element_uniqueids:
                 print self.get_object(uid)).__str__() + "\n"
            
     '''
    def __init__(self, element_ids, alledges, get_object): 
        ''' element_ids is a list of the uniqueids of the elements to go in this block [id1,id2,...]
            alledges is a dictionary of all the Edges in the event
            get_object allows access to the underlying elements given a uniqueid  
        '''
        #make a uniqueid for this block
        self.uniqueid = Identifier.make_id(self,Identifier.PFOBJECTTYPE.BLOCK) 
        
        #allow access to the underlying object
        self.get_object = get_object        
        
        #order the elements by element type (ecal, hcal, track) and then by element id         
        self.element_uniqueids =sorted(element_ids, key =lambda  x: Identifier.type_short_code(x) + str(x) )
        
        #extract the relevant parts of the complete set of edges and store this within the block
        self.edges = dict()       
        for id1, id2 in itertools.combinations(self.element_uniqueids,2):
            key = Edge.make_key(id1,id2)
            self.edges[key] = alledges[key]
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
    
    def elements_string(self) : 
        ''' Construct a string descrip of each of the elements in a block '''
        count = 0
        elemdetails = "\n      elements: {\n"  
        for uid in self.element_uniqueids:
            elemname = Identifier.type_short_code(uid) +str(count)
            elemdetails += "      " + elemname + ": " + (self.get_object(uid)).__str__() + "\n"
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
        descrip = str('\n      ecals = {count_ecal} hcals = {count_hcal} tracks = {count_tracks}'.format(
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
    ''' BlockBuilder takes a set of particle flow elements (clusters,tracks etc)
        and uses the distances between elements to construct a set of blocks
        Each element will end up in one (and only one block)
        Blocks retain information of the elements and the distances between elements
        The blocks can then be used for future particle reconstruction
        
        attributes:
        
        blocks  : dictionary of blocks {id1:block1, id2:block2, ...}
        history_nodes : dictionary of nodes that describe which elements are parents of which blocks 
                        if an existing history_nodes tree  eg one created during simulation
                        is passed to the BlockBuilder then
                        the additional history will be added into the exisiting history 
        nodes :    dictionary of nodes which describes the distances/links between elements
                 the nodes dictionary is used to create the blocks
    
        
        Usage example:

            builder = BlockBuilder(tracks, ecal, hcal,ruler,get_object)
            for b in builder.blocks.itervalues() :
                print b
    '''
    def __init__(self,  tracks, ecal, hcal, ruler, get_object, hist_nodes = None):
        '''describe what the method is doing.. here ok because constructor
        describe what is expected for parameters, e.g. dictionary for tracks, ecal
        hcal.
        say also what method is returning.

        tracks is a dictionary : {id1:track1, id2:track2, ...}
        ecal is a dictionary : {id1:ecal1, id2:ecal2, ...}
        hcal is a dictionary : {id1:hcal1, id2:hcal2, ...}
        ruler is something that measures distance between two objects eg track and hcal
            (see Distance class for example)
            it should take the two objects as arguments and return a tuple
            of the form
                link_type = 'ecal_ecal', 'ecal_track' etc
                is_link = true/false
                distance = float
        hist_nodes is an optional dictionary of Nodes : { id:Node1, id: Node2 etc}
            it could for example contain the simulation history nodes
            A Node contains the id of an item (cluster, track, particle etc)
            and says what it is linked to (its parents and children)
            if hist_nodes is provided it will be added to with the new block information
            If hist_nodes is not provided one will be created, it will contain nodes
            corresponding to each of the tracks, ecal etc and also for the blocks that
            are created by the block builder.
        '''
        
        #given a unique id this can return the underying object
        self.get_object = get_object

        # if the user does not specify an existing history tree,
        # start the tree with the identifiers of the provided tracks,
        # ecal and hcal clusters
        self.history_nodes = hist_nodes
        if self.history_nodes is None:
            self.history_nodes = dict(
                self._make_dict(tracks).items() + 
                self._make_dict(ecal).items() +
                self._make_dict(hcal).items() )

        # build the block nodes (separate graph which will use distances between items to determine links)
        self.nodes = dict(
             self._make_dict(tracks).items() + 
             self._make_dict(ecal).items() +
             self._make_dict(hcal).items() )
        
        # compute link properties between each pair of nodes
        self.edges = dict()
        for id1, id2 in itertools.combinations(self.nodes,2) :
            edge=self._make_edge(id1,id2, ruler)
            #the edge object is added into the edges dictionary
            self.edges[edge.key] = edge
            #add linkage info into the nodes dictionary
            if  edge.linked: #this is actually an undirected link - OK for undirected searches 
                self.nodes[id1].add_child(self.nodes[id2])            

        # build the blocks of connected nodes
        self.blocks = dict()
        self._make_blocks()

        
    def _make_dict(self, elems):  # this method is made private by the start _
        '''for a list of identifiers, return a dictionary
        {identifier: Node(identifier)}
        '''
        return dict( (idt, Node(idt)) for idt in elems )
    
    def _make_edge(self,id1,id2, ruler):
        ''' id1, id2 are the unique ids of the two items
            an edge object is returned which contains the link_type, is_link (bool) and distance between the 
            objects. 
        '''
        #find the original items and pass to the ruler to get the distance info
        obj1 = self.get_object(id1)
        obj2 = self.get_object(id2)
        link_type, is_linked, distance = ruler(obj1,obj2)
        
        #make the edge and add the edge into the dict 
        return Edge(id1,id2, link_type,is_linked, distance) 
        
    def _make_blocks (self) :
        ''' uses the DAGfloodfill algorithm in connection with the BlockBuilder nodes
            to work out which elements are connected
            Each set of connected elements will be used to make a new PFBlock
        ''' 
        for b in DAGFloodFill(self.nodes).blocks :
            rec_history_UIDs = [] 
            elem_descrips = []
            # NB the nodes that are found by FloodFill are the Nodes describing links between items
            # we acually want the blocks to contain the corresponding history nodes 
            # So, find the corresponding history nodes
            for e in b :
                rec_history_UIDs.append(e.get_value())
                #elem_descrips.append(self.get_object(e.get_value()).__str__())

            #now we can make the block
            block = PFBlock(rec_history_UIDs,  self.edges, self.get_object) #pass the edgedata and extract the needed edge links for this block          
           
            #put the block in the dict of blocks            
            self.blocks[block.uniqueid] = block        
            
            #make a node for the block and add into the history Nodes
            blocknode = Node(block.uniqueid)
            self.history_nodes[block.uniqueid] = blocknode
            
            #now add in the links between the block elements and the block into the history_nodes
            for elemid in block.element_uniqueids :
                self.history_nodes[elemid].add_child(blocknode)            
                     
    
        
            
    def __str__(self):
        descrip = "{ " 
        for block in self.blocks.iteritems() :
            #print "block " , block  , "endblock"
            descrip = descrip + block.__str__()
        descrip = descrip + "}\n"
        return descrip  
    
    def __repr__(self):
        return self.__str__()      
  
#
#What is the purpose of the class? 
#    describe interface, and in particular what are the# 
#    important attributes that the user can find in this class
#    give a usage example.$tell how to use the blocks (code fragment)
#
#    review all methods : pythonic name e.g. make_history_node 
#    think about what has to be private or exposed to the user
#    same for attributes