import itertools
from heppy.papas.graphtools.graphbuilder import GraphBuilder
from heppy.papas.graphtools.edge import Edge
from heppy.papas.graphtools.DAG import Node
from heppy.papas.pfobjects import MergedCluster

class MergedClusterBuilder(GraphBuilder):
    ''' MergingBlockBuilder takes particle flow elements of one cluster type eg ecal_in
        and uses the distances between elements to construct a set of blocks ( of connected clusters)
        The blocks will contain overlapping clusters and then be used to merge the clusters
        
        attributes:
             merged - the dictionary of merged clusters
        
        Usage example:
             (will return the merged clusters to the event)
            event.ecal_clusters =  MergingBlockBuilder(event.ecal_clusters, ruler).merged
            
    '''
    def __init__(self, clusters, ruler, history_nodes = None):
        '''
        clusters a dictionary : {id1:ecal1, id2:ecal2, ...}
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
        self.clusters = clusters
        
        # the merged clusters will be stored here
        self.merged = dict()
        # collate ids of clusters
        uniqueids = list(clusters.keys())         
             
        
        # compute edges between each pair of nodes
        edges = dict()
        for obj1, obj2 in itertools.combinations(clusters.values(),2):
            link_type, is_linked, distance = ruler(obj1, obj2)
            edge = Edge(obj1.uniqueid, obj2.uniqueid, is_linked, distance)
            #the edge object is added into the edges dictionary
            edges[edge.key] = edge
            
        #make the subgraphs of clusters
        super(MergedClusterBuilder, self).__init__(uniqueids,edges)
        
        #make sure we use the original history and update it as needed
        self.history_nodes = history_nodes
            
        self._make_merged_clusters()
        
    def _make_merged_clusters(self):
        #carry out the merging of linked clusters
        for subgraphids in self.subgraphs:
            if len(subgraphids)==1 : 
                #no overlapping cluster so no merging needed
                self.merged[subgraphids[0]] = self.clusters[subgraphids[0]]
            else: 
                #make a merged "supercluster" and then add each of the linked clusters into it                
                supercluster = None
                for elemid in subgraphids :
                    thing = self.clusters[elemid]
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
                        

