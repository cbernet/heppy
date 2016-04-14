import itertools
from blockbuilder import BlockBuilder
from edge import Edge
from DAG import Node
from heppy.papas.pfobjects import MergedCluster

class MergedClusterBuilder(GraphBuilder):
    ''' MergingBlockBuilder takes particle flow elements of one cluster type eg ecal_in
        and uses the distances between elements to construct a set of blocks ( of connected clusters)
        The blocks will contain overlapping clusters and then be used to merge the clusters
        
        attributes:
             merged - the dictionary of merged clusters
        
        Usage example:
             (will return the merged clusters to the event)
            event.ecal_clusters =  MergingBlockBuilder("ecal_in",PFEvent(event), ruler).merged
            
    '''
    def __init__(self, layer, pfevent, ruler, history_nodes = None):
        '''
        pfevent is event structure inside which we find
            tracks is a dictionary : {id1:track1, id2:track2, ...}
            ecal is a dictionary : {id1:ecal1, id2:ecal2, ...}
            hcal is a dictionary : {id1:hcal1, id2:hcal2, ...}
            get_object() which allows a cluster or track to be found from its id
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
            are created by the event block builder.
        '''
        
        #given a unique id this can return the underying object
        self.pfevent = pfevent
        
        # the merged clusters will be stored here
        self.merged =dict()

        # collate ids of clusters
        if layer=="ecal_in":
            uniqueids = list(pfevent.ecal_clusters.keys())         
        elif layer=="hcal_in":
            uniqueids = list(pfevent.hcal_clusters.keys())         
             
        
        # compute edges between each pair of nodes
        edges = dict()
        for id1, id2 in itertools.combinations(uniqueids,2):
            edge = self._make_edge(id1,id2, ruler)
            #the edge object is added into the edges dictionary
            edges[edge.key] = edge
            
        #make he subgraphs of clusters
        super(MergedClusterBuilder, self).__init__(uniqueids,edges)
        
        #make sure we use the original history and update it as needed
        self.history_nodes = history_nodes
        if history_nodes is None:
            self.history_nodes =  dict( (idt, Node(idt)) for idt in uniqueids )             
        
        self._make_merged_clusters()
        
    def _make_merged_clusters(self):
        #carry out the merging of linked clusters
        for subgraphids in self.subgraphs:
            if len(subgraphids)==1 : 
                #no overlapping cluster so no merging needed
                self.merged[subgraph[0]] = self.pfevent.get_object(subgraphids[0)
            else: 
                #make a merged "supercluster" and then add each of the linked clusters into it                
                supercluster = None
                for elemid in subgraphids :
                    thing = self.pfevent.get_object(elemid)
                    if supercluster is None:
                        supercluster = MergedCluster(thing)
                        self.merged[supercluster.uniqueid] = supercluster
                        
                        if (self.history_nodes): 
                            #update the history
                            snode = Node(supercluster.uniqueid)
                            self.history_nodes[supercluster.uniqueid] = snode
                            #now add in the links between the block elements and the block into the history_nodes
                            self.history_nodes[elemid].add_child(snode)
                        continue
                    else: 
                        supercluster += thing
                        if (self.history_nodes):
                            self.history_nodes[elemid].add_child(snode)  
                        

    def _make_edge(self,id1,id2, ruler): # should I put this in blockbuilder as is used here and in PFBlockBuilder
        ''' id1, id2 are the unique ids of the two items
            ruler is something that measures distance between two objects eg track and hcal
            (see Distance class for example)
            it should take the two objects as arguments and return a tuple
            of the form
                link_type = 'ecal_ecal', 'ecal_track' etc
                is_link = true/false
                distance = float
            an edge object is returned which contains the link_type, is_link (bool) and distance between the 
            objects. 
        '''
        #find the original items and pass to the ruler to get the distance info
        obj1 = self.pfevent.get_object(id1)
        obj2 = self.pfevent.get_object(id2)
        link_type, is_linked, distance = ruler(obj1,obj2) #some redundancy in link_type as both distance and Edge make link_type
                                                          #not sure which to get rid of
        
        #make the edge and add the edge into the dict 
        return Edge(id1,id2, is_linked, distance) 
        
    
