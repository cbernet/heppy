import itertools
from heppy.papas.graphtools.graphbuilder import GraphBuilder
from heppy.papas.graphtools.edge import Edge
from heppy.papas.graphtools.DAG import Node
from heppy.papas.pfobjects import MergedCluster
from heppy.papas.data.identifier import Identifier
from heppy.utils.pdebug import pdebugger

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
        uniqueids = sorted(list(clusters.keys()))         
             
        #make the edges match cpp by using a the same approach as cpp
        ## compute edges between each pair of nodes
        #
        #for obj1, obj2 in itertools.combinations(clusters.values(),2):
            #link_type, is_linked, distance = ruler(obj1, obj2)
            #edge = Edge(obj1.uniqueid, obj2.uniqueid, is_linked, distance)
            ##the edge object is added into the edges dictionary
            #edges[edge.key] = edge
            
        edges = dict() #OrderedDict()    
        for obj1 in  clusters.values():
            for obj2 in  clusters.values():
                if obj1.uniqueid < obj2.uniqueid :
                    #if Identifier.pretty(obj1.uniqueid)=="e310" or Identifier.pretty(obj2.uniqueid)=="e310":
                    #    print Identifier.pretty(obj2.uniqueid)
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
            subgraphids.sort()
            if len(subgraphids)==5:
                pass
            #make a mergecluster based on the first cluster
            id =  subgraphids[0] # first id in list
            if (len(subgraphids)>1):
                for  sid in subgraphids : 
                    pdebugger.info('Merged Cluster from {}'.format(self.clusters[sid]))
            #make a merged cluster based on the first cluster and create a new Id for it.
            supercluster = MergedCluster(self.clusters[id]) # Identifier.make_id(Identifier.get_type(id)));
            self.merged[supercluster.uniqueid] = supercluster;
            if (self.history_nodes) : 
                #update the history
                snode = Node(supercluster.uniqueid)
                self.history_nodes[supercluster.uniqueid] = snode
                self.history_nodes[id].add_child(snode)
            if len(subgraphids)>1 : 
                #add each of the linked clusters into it                
                for elemid in subgraphids :
                    if elemid != id : # we have already handled this one
                        thing = self.clusters[elemid]
                        #now add in the links between the block elements and the block into the history_nodes
                        self.history_nodes[elemid].add_child(snode)
                        supercluster += thing
            if (len(subgraphids)>1):
                pdebugger.info(str('Made {}\n'.format(supercluster)))

