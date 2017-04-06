from heppy.papas.graphtools.subgraphbuilder import SubgraphBuilder
from heppy.papas.graphtools.edge import Edge
from heppy.papas.graphtools.DAG import Node
from heppy.papas.pfobjects import MergedCluster
from heppy.utils.pdebug import pdebugger

class MergedClusterBuilder(SubgraphBuilder):
    ''' MergedClusterBuilder takes particle flow elements of one cluster type eg ecal_in
        and uses the distances between elements to construct a set of blocks ( of connected clusters).
        The blocks will contain overlapping clusters and then be used to merge the clusters.
        
        attributes:
             merged - the dictionary of merged clusters.
        
        Usage example:
             This will return the merged clusters to the event.
            event.ecal_clusters =  MergingBlockBuilder(event.ecal_clusters, ruler.merged_clusters
            
    '''
    def __init__(self, clusters, ruler, history_nodes):
        '''
        @param clusters: a dictionary : {id1:ecal1, id2:ecal2, ...}.
        @param ruler: measures distance between two clusters,
            see Distance class for example.
            It should take the two objects as arguments and return a tuple
            of the form:
                link_type = 'ecal_ecal'
                is_link = true/false
                distance = float
        @param history_nodes: a dictionary of Nodes : { id:Node1, id: Node2 etc}.
            It could for example contain the simulation history nodes.
            A Node contains the id of a cluster.
            and says what it is linked to (its parents and children).
            New mergedcluster history detailing which clusters the mergedcluster was made from
            will be added to the existing history
        '''
        self.clusters = clusters
        
        # the merged clusters will be stored here
        self.merged_clusters = dict()

        # collate ids of clusters
        uniqueids = list(clusters.keys())
             
        #make the edges match cpp by using the same approach as cpp
        edges = dict()
        for obj1 in  clusters.values():
            for obj2 in  clusters.values():
                if obj1.uniqueid < obj2.uniqueid:
                    link_type, is_linked, distance = ruler(obj1, obj2)
                    edge = Edge(obj1.uniqueid, obj2.uniqueid, is_linked, distance)
                    #the edge object is added into the edges dictionary
                    edges[edge.key] = edge

        #make the subgraphs of clusters
        super(MergedClusterBuilder, self).__init__(uniqueids, edges)
        
        #make sure we use the original history and update it as needed
        self.history_nodes = history_nodes
        self._make_and_store_merged_clusters()

    def _make_and_store_merged_clusters(self):
        '''
            This takes the subgraphs of connected clusters that are to be merged, and makes a new MergedCluster.
            It stores the new MergedCluser into the self.merged_clusters collection.
            It then updates the history to record the links between the clusters and the merged cluster.
        '''
        for subgraph in self.subgraphs: # TODO may want to order subgraphs from largest to smallest at some point
            subgraph.sort(reverse=True) #start with highest E or pT clusters
            overlapping_clusters = [self.clusters[node_id] for node_id in subgraph]
            supercluster = MergedCluster(overlapping_clusters, len(self.merged_clusters))
            self.merged_clusters[supercluster.uniqueid] = supercluster
            if self.history_nodes:
                snode = Node(supercluster.uniqueid)
                self.history_nodes[supercluster.uniqueid] = snode
                for node_id in subgraph:
                    self.history_nodes[node_id].add_child(snode)
            pdebugger.info(str('Made {}'.format(supercluster)))
