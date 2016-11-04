
'''Produces plots of Papas Directed Acyclic Graphs'''
import pydot
from heppy.papas.data.identifier import Identifier
from heppy.papas.data.historyhelper import HistoryHelper

class DagPlotter(object):
    '''   
           Object to assist with plotting directed acyclic graph histories.
          
           Usage:
           histplot = DagPlotter(papapasevent, detector)
           histplot.plot_dag("event")     #write dag event plot to file   
           histplot.plot_dag("subgroups", num_subgroups=3 ) #write dag subevent plots to file

        '''        
    def __init__(self, papasevent, directory):
        '''
        * papasevent is a PapasEvent
        * diretory is where the output plots go
        '''
        self.papasevent = papasevent  
        self.helper = HistoryHelper(papasevent)
        self.directory = directory  
    
    def plot_dag(self, plot_type, num_subgroups=None, show_file=False): 
        '''DAG plot for an event
        @param plot_type: "event" everything in event or "subgroups" one or more connected subgroups
        @param num_subgroups: if specified then the num_subgroups n largest subgroups are plotted
        otherwise all subgroups are plotted
        @param show_file: whether to display file on screen after making it (NB it only operates when plot_type is "event")
        '''
        if plot_type == "event": #dag for whole event
            ids = self.helper.event_ids()
            filename = 'event_' + str(self.papasevent.iEv) + '_dag.png' 
            self.plot_dag_ids(ids, filename, show_file)   
        elif plot_type == "subgroups":
            subgraphs = self.helper.get_history_subgroups()
            if num_subgroups is None:
                num_subgroups = len(subgraphs)
            else:
                num_subgroups = min(num_subgroups, len(subgraphs))            
            for i in range(num_subgroups): #one plot per subgroup
                filename = 'event_' + str(self.papasevent.iEv)  +'_subgroup_' + str(i) + '_dag.png' 
                self.plot_dag_ids(subgraphs[i], filename)    
                
    def plot_dag_ids(self, ids, filename, show_file=False):
        '''DAG plot will be produced and sent to file for a set of ids
        @param ids: list of ids to be included in the DAG plot
        @param filename: output filename
        @param show_file: whether to open file and show on screen
        '''
        graph = pydot.Dot(graph_type='digraph')   
        self._graph_ids(ids, graph)        
        namestring = '/'.join([self.directory, filename])    
        graph.write_png(namestring) 
        if show_file:
            call(["open", namestring])      
        
    def _graph_ids(self, nodeids, graph):
        '''creates graphnodes and graph edges for the dag dot plot based on the nodes supplied
        
        @param nodeids: which ids should go on the plot
        @param graph: the dot plot graph into which the plot nodes will be added'''
        graphnodes = dict() 
        for nodeid in nodeids: #first create the collection of nodes
            node = self.papasevent.history[nodeid]
            if  not graphnodes.has_key(self.pretty(node)):
                graphnodes[self.pretty(node)] = pydot.Node(self.pretty(node), style="filled", label=self.short_info(node), fillcolor=self.color(node))
                graph.add_node(graphnodes[self.pretty(node)]) 
        #once all the nodes are made we can now build the edges
        for nodeid in nodeids:
            node = self.papasevent.history[nodeid]
            for c in node.parents:
                if len(graph.get_edge(graphnodes[self.pretty(c)], graphnodes[self.pretty(node)])) == 0:
                    graph.add_edge(pydot.Edge(graphnodes[self.pretty(c)], graphnodes[self.pretty(node)]))
            if self.type_and_subtype(node) == 'bs': # also create block topological links
                bl = self.object(node)
                if len(bl.element_uniqueids) > 1:
                    self._graph_add_topological_block(graph, graphnodes, bl)     
                    
    def _graph_add_topological_block(self, graph, graphnodes, pfblock):
        '''this adds the block links (distance, is_linked) onto the DAG in red'''
        for edge in pfblock.edges.itervalues():
            if  edge.linked: 
                label = "{:.1E}".format(edge.distance)
                if edge.distance == 0:
                    label = "0"
                graph.add_edge(pydot.Edge(graphnodes[Identifier.pretty(edge.id1)],
                                          graphnodes[Identifier.pretty(edge.id2)],
                                          label=label, style="dashed", color="red", arrowhead="none", arrowtail="none", fontsize='7'))
    
    def pretty(self, node):
        ''' pretty form of the unique identifier
        @param node: a node in the DAG history'''
        return Identifier.pretty(node.get_value())
    
    def type_and_subtype(self, node):
        ''' Return two letter type and subtype code for a node For example 'pg', 'ht' etc
        @param node: a node in the DAG history'''
        return Identifier.type_and_subtype(node.get_value()) 

    def short_info(self, node):
        '''used to label plotted dag nodes
        @param node: a node in the DAG history'''
        obj = self.object(node)
        return Identifier.pretty(obj.uniqueid) + "\n " +obj.short_info()        

    def color(self, node):
        '''used to color dag nodes
        @param node: a node in the DAG history'''
        cols = ["red", "lightblue", "green", "yellow", "cyan", "grey", "white", "pink"]
        return cols[Identifier.get_type(node.get_value())]                     

    def object(self, node):
        '''returns object corresponding to a node
        @param node: a node in the DAG history'''
        z = node.get_value()
        return self.papasevent.get_object(z)          

