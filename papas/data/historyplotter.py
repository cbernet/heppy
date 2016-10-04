class HistoryPlotter(object):
    def __init__(self, papasevent):
        #this information information needed to be able to unravel information based on a unique identifier
        self.history_nodes = papasevent.history
        self.papasevent = papasevent      
        
    def plot_event(self, event):
        z = node.get_value()
        return Identifier.pretty(z)
    
    def short(self, node):
        z = node.get_value()
        return Identifier.type_code(z) 
        
    def short_info(self, node):
        obj=self.object(node)
        return Identifier.type_code(obj.uniqueid) +obj.shortinfo()       
       
    def color(self, node):
        cols =["red", "lightblue", "green", "yellow","cyan", "grey", "white","pink"]
        intcols =[1,2,3,4,5,6,7,8]
        return cols[Identifier.get_type(node.get_value())]            
            
    def intcolor(self, node):
        intcols =[1,2,3,4,5,6,7,8]
        return intcols[Identifier.get_type(node.get_value())]            

    def object(self, node):
        z = node.get_value()
        return self.papasevent.get_object(z) 
              
    def graph_items (self, ids):
        #DAG plot for set of ids
        #input:
        #   ids: list of uniqueids
        graph = pydot.Dot(graph_type='digraph')   
        self._graph_ids(ids, graph)
        namestring='graphs/event_' + str(self.papasevent.iEv) +'_item_' + Identifier.pretty(ids[0]) + '_dag.png'
        graph.write_png(namestring) 
    
    def graph_event(self, nodeids): 
        #DAG plot for whole event
        #input:
         #   ids: list of uniqueids  for full event      
        graph = pydot.Dot(graph_type='digraph')             
        self._graph_ids(nodeids, graph)
        namestring = 'graphs/event_' + str(self.papasevent.iEv)  + '_dag.png'
        graph.write_png(namestring)    
        
    def _graph_add_block (self,graph, graphnodes, pfblock):
        #this adds the block links (distance, is_linked) onto the DAG in red
        intcols =[1,2,3,4,5,6,7,8]
        for edge in pfblock.edges.itervalues():
            if  edge.linked: 
                graph.add_edge(pydot.Edge(  graphnodes[Identifier.pretty(edge.id1)],graphnodes[Identifier.pretty(edge.id2)],
                label=round(edge.distance,1),style="dashed", color="red",arrowhead="none",arrowtail="none",fontsize='7' ))
        pass      
                         
    def _graph_ids (self, nodeids, graph):
        graphnodes = dict() 
        for nodeid in nodeids:
            node = self.history_nodes[nodeid]
            if  graphnodes.has_key(self.short_name(node))==False:
                graphnodes[self.short_name(node)] = pydot.Node(self.short_name(node), style="filled", label=self.short_info(node), fillcolor=self.color(node))
                graph.add_node( graphnodes[self.short_name(node)]) 
        for nodeid in nodeids:
            node = self.history_nodes[nodeid]
            for c in node.parents:
                if len(graph.get_edge(graphnodes[self.short_name(c)],graphnodes[self.short_name(node)]))==0:
                    graph.add_edge(pydot.Edge(  graphnodes[self.short_name(c)],graphnodes[self.short_name(node)])) 
                    
        for nodeid in nodeids:
            node = self.history_nodes[nodeid]
            if self.short(node)== 'b':
                bl=self.object(node)
                if len(bl.element_uniqueids)>1:
                    self._graph_add_block(graph, graphnodes, bl)             
             
    def graph_event_root(self, nodeids): 
        #DAG for whole event (not very good when printed)
        from ROOT import TGraphStruct,TGraphNode, TGraphEdge, gPad, TCanvas
        can=TCanvas("History","c",2000,1200)        
        graph = TGraphStruct()
        self._graph_ids_root(nodeids, graph)
        graph.Draw()
        can.Draw()
        gPad.Update()
        gPad.SaveAs('event_' + str(self.papasevent.iEv) + '_root_dag.png')   
        pass
    
    def graph_items_root (self, ids):
        #DAG for group of ids
        from ROOT import TGraphStruct,TGraphNode, TGraphEdge, gPad, TCanvas
        can=TCanvas("History","c",600,600)       
        graph = TGraphStruct() 
        self._graph_ids_root (ids, graph)
        graph.Draw()
        can.Draw()
        gPad.Update()
        gPad.SaveAs('event_' + str(self.papasevent.iEv)+ '_item_' + Identifier.pretty(ids[0]) + '_root_dag.png')   
        
    
    def _graph_ids_root (self, nodeids,graph ):  
        from ROOT import TGraphStruct,TGraphNode, TGraphEdge, gPad, TCanvas
        graphnodes=dict()
        for nodeid in nodeids:
            node = self.history_nodes[nodeid]
            if   graphnodes.has_key(self.short_name(node))==False:
                n=TGraphNode(self.short_name(node), self.short_info(node))
                graphnodes[self.short_name(node)] = n
                n.SetFillColor(self.intcolor(node))
                n.SetTextSize(0.02)
                graph.AddNode( graphnodes[self.short_name(node)])
        for nodeid in nodeids:
            node = self.history_nodes[nodeid]
            for c in node.parents:
                edge=TGraphEdge(graphnodes[self.short_name(c)],graphnodes[self.short_name(node)])
                edge.SetLineStyle(1)
                graph.AddEdge( edge)
        for nodeid in nodeids:
            node = self.history_nodes[nodeid]
            if self.short(node)== 'b':
                bl=self.object(node)
                if len(bl.element_uniqueids)>2:
                    self.graph_add_block_root(graph, graphnodes, bl)
        pass
    
    def graph_add_block_root(self,graph, graphnodes, pfblock):
        #this documents the pfblock linkages in red (need to add distance text for root)
        from ROOT import TGraphStruct,TGraphNode, TGraphEdge    
    
        for edge in pfblock.edges.itervalues():
            if  edge.linked: 
                edge=TGraphEdge(graphnodes[Identifier.pretty(edge.id1)],graphnodes[Identifier.pretty(edge.id2)])
                edge.SetLineStyle(2)
                edge.SetLineColor(2)
                graph.AddEdge( edge) 
    
        pass    

        