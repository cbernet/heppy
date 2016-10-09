from heppy.papas.data.identifier import Identifier
import pydot
from heppy.papas.data.historyhelper import HistoryHelper
from subprocess import call
from heppy.display.core import Display
from heppy.display.geometry import GDetector
from heppy.display.pfobjects import GTrajectories, GHistoryBlock

class HistoryPlotter(object):
    '''   
           Object to assist with plotting histories.
           It allows extraction of information from the papasevent
    
           Usage:
           hist = HistoryHelper(papasevent)
           histplot = HistoryPlotter(papapasevent, detector, True)
           histplot.plot_event_compare() 
           histplot.plot_dag_event(True)        
           histplot.plot_dag_subgroups(top=3 , True) 
    
    
        '''        
    def __init__(self, papasevent, detector, is_display):
        '''
        * papasevent is a PapasEvent
        * detector
        * is_display True/False
        
        '''
        self.history = papasevent.history
        self.papasevent = papasevent  
        self.helper = HistoryHelper(papasevent)
        self.detector = detector
        self.is_display = is_display
        if self.is_display:
            self.init_display()        

    def init_display(self):
        #double paned Display
        #make this a choice via parameters somehow
        self.display = Display(['xy','yz'], pads=("simulated", "reconstructed"))
        self.gdetector = GDetector(self.detector)
        self.display.register(self.gdetector, layer=0, clearable=False)        
        
    def pretty(self, node):
        ''' pretty form of the unique identifier'''
        return Identifier.pretty(node.get_value())
    
    def type_and_subtype(self, node):
        ''' For example 'pg', 'ht' etc'''
        return Identifier.type_and_subtype(node.get_value()) 
        
    def short_info(self, node):
        '''used to label plotted dag nodes'''
        obj=self.object(node)
        return Identifier.pretty(obj.uniqueid) + "\n " +obj.shortinfo()        
       
    def color(self, node):
        '''used to color dag nodes'''
        cols =["red", "lightblue", "green", "yellow","cyan", "grey", "white","pink"]
        intcols =[1,2,3,4,5,6,7,8]
        return cols[Identifier.get_type(node.get_value())]                     

    def object(self, node):
        '''returns object corresponding to a node'''
        z = node.get_value()
        return self.papasevent.get_object(z) 

    def plot_event(self):
        '''Event plot containing Simulated particles and smeared clusters 
        '''
        if self.is_display  :
            #whole event as DAG
            history=self.papasevent.history
            particles = self.papasevent.get_collection('ps')
            ecals = self.helper.get_collection(ids,'es')
            hcals = self.helper.get_collection(ids,'hs')             
            self.display.clear()  
            self.display.register( GHistoryBlock(particles, ecals, hcals, self.detector,  is_grey), layer=layer, sides = [position])            
            self.display.draw()       
            gPad.SaveAs('graphs/event_' + str(event.iEv) + '_sim.png')  

    def plot_event_compare(self):
        '''Double event plot for full event
            containing Simulated particles and smeared clusters on left
            and reconstructed particles and merged clusters on right side
            '''    
        self.display.clear()       
        self._plot_ids_compare(self.helper.event_ids())             
        self.display.draw() 
        pass  
        
    def plot_subgroup_compare(self, ids):
        '''Double event plot for a subgroup of an event
                containing Simulated particles and smeared clusters on left
                and reconstructed particles and merged clusters on right side
                    '''          
        if self.is_display  :
            self.display.clear()       
            self._plot_ids_compare(ids)
            self.display.draw() 
            pass   
        
    def _plot_ids_compare(self, ids, offset = 0):
        #handles plotting the sim and rec particles on a double event plot
        sim_particles = self.helper.get_collection(ids, 'ps')
        rec_particles = self.helper.get_collection(ids,'pr')
        sim_ecals = self.helper.get_collection(ids,'es')
        sim_hcals = self.helper.get_collection(ids,'hs') 
        rec_ecals = self.helper.get_collection(ids,'em')
        rec_hcals = self.helper.get_collection(ids,'hm')             
        self._add_particles(sim_particles, sim_ecals, sim_hcals, position= 0 + offset*2, is_grey = False, layer = 2)
        self._add_particles(sim_particles, sim_ecals, sim_hcals, position= 1 + offset*2, is_grey = True, layer = 1)
        self._add_particles(rec_particles, rec_ecals, rec_hcals, position= 0 + offset*2, is_grey = True, layer = 1)
        self._add_particles(rec_particles, rec_ecals, rec_hcals, position= 1 + offset*2, is_grey = False, layer = 2)   
    
        
    def _add_particles(self, particles, ecals, hcals, position, is_grey=False , layer = 1):
        self.display.register( GHistoryBlock(particles, ecals, hcals, self.detector,  is_grey), layer=layer, sides = [position]) 
         
    def plot_subevents_compare(self):
        ''' An experiment to plot largest 8 subgroups in an event all at once'''
        if self.is_display:
            self.display.clear() 
            
            
            subgraphs=self.helper.get_history_subgroups()  
            subsize = len(subgraphs)
            from itertools import product
            subgraphs.sort(key = lambda s: -len(s))
            ids = []
            for i in range(0, 8):
                ids.append( Identifier.pretty(subgraphs[i][0]))
            lists = [ ids ,["simulated", "reconstructed"]]
            result = ['_'.join(map(str,x)) for x in product(*lists)]   
            self.display = Display(['xy','yz'], pads=result)
            self.display.register(self.gdetector, layer=0, clearable=False)             
            
            for i in range(0, 8):     
                s = subgraphs[i]
                self._plot_ids_compare(s, offset = i)      
        self.display.draw()         
        #gPad.SaveAs('graphs/event_' + str(self.event.iEv) + '_sim_rec_compare.png') 
                             
              
    def plot_dag_ids (self, ids, show = True):
        '''DAG plot for a set of ids
        '''
        graph = pydot.Dot(graph_type='digraph')   
        self._graph_ids(ids, graph)
        namestring='graphs/event_' + str(self.papasevent.iEv) +'_item_' + Identifier.pretty(ids[0]) + '_dag.png'
        graph.write_png(namestring) 
        if show:
            call(["open", namestring])        
    
    def plot_dag_event(self, show = False): 
        '''DAG plot for an event
        '''
        ids = self.helper.event_ids()
        graph = pydot.Dot(graph_type='digraph')             
        self._graph_ids(ids, graph)
        namestring = 'graphs/event_' + str(self.papasevent.iEv)  + '_dag.png'
        graph.write_png(namestring) 
        if show:
            call(["open", namestring])
            
    def plot_dag_subgroups(self, top = None, show = False):
        '''produces DAG plots of event subgroups (one per subgroup)
           If top is specified then the top n largest subgroups are plotted
           otherwise all subgroups are plotted
        '''
        if self.is_display  :
            subgraphs=self.helper.get_history_subgroups()  
            if top is None:
                top = len(subgraphs)
            for i in range(top):   
                self.plot_dag_ids(subgraphs[i], show)       
        
    def _graph_add_block (self,graph, graphnodes, pfblock):
        #this adds the block links (distance, is_linked) onto the DAG in red
        intcols =[1,2,3,4,5,6,7,8]
        for edge in pfblock.edges.itervalues():
            if  edge.linked: 
                graph.add_edge(pydot.Edge(  graphnodes[Identifier.pretty(edge.id1)],graphnodes[Identifier.pretty(edge.id2)],
                label=round(edge.distance,1),style="dashed", color="red",arrowhead="none",arrowtail="none",fontsize='7' ))
        pass      
                         
    def _graph_ids (self, nodeids, graph):
        #creates graphnodes and graph edges for the dot plot based on the nodes
        graphnodes = dict() 
        for nodeid in nodeids:
            node = self.history[nodeid]
            if  graphnodes.has_key(self.pretty(node))==False:
                graphnodes[self.pretty(node)] = pydot.Node(self.pretty(node), style="filled", label=self.short_info(node), fillcolor=self.color(node))
                graph.add_node( graphnodes[self.pretty(node)]) 
        for nodeid in nodeids:
            node = self.history[nodeid]
            for c in node.parents:
                if len(graph.get_edge(graphnodes[self.pretty(c)],graphnodes[self.pretty(node)]))==0:
                    graph.add_edge(pydot.Edge(  graphnodes[self.pretty(c)],graphnodes[self.pretty(node)])) 
                    
        for nodeid in nodeids:
            node = self.history[nodeid]
            if self.type_and_subtype(node)== 'bs':
                bl=self.object(node)
                if len(bl.element_uniqueids)>1:
                    self._graph_add_block(graph, graphnodes, bl) 
                    
  
#The following documents experiments with root dot plot and matplotlib  
             
    #def graph_event_root(self, nodeids): 
        ##DAG for whole event (not very good when printed)
        #from ROOT import TGraphStruct,TGraphNode, TGraphEdge, gPad, TCanvas
        #can=TCanvas("History","c",2000,1200)        
        #graph = TGraphStruct()
        #self._graph_ids_root(nodeids, graph)
        #graph.Draw()
        #can.Draw()
        #gPad.Update()
        #gPad.SaveAs('event_' + str(self.papasevent.iEv) + '_root_dag.png')   
        #pass
    
    #def graph_items_root (self, ids):
        ##DAG for group of ids
        #from ROOT import TGraphStruct,TGraphNode, TGraphEdge, gPad, TCanvas
        #can=TCanvas("History","c",600,600)       
        #graph = TGraphStruct() 
        #self._graph_ids_root (ids, graph)
        #graph.Draw()
        #can.Draw()
        #gPad.Update()
        #gPad.SaveAs('event_' + str(self.papasevent.iEv)+ '_item_' + Identifier.pretty(ids[0]) + '_root_dag.png')   
        
    
    #def _graph_ids_root (self, nodeids,graph ):  
        #from ROOT import TGraphStruct,TGraphNode, TGraphEdge, gPad, TCanvas
        #graphnodes=dict()
        #for nodeid in nodeids:
            #node = self.history[nodeid]
            #if   graphnodes.has_key(self.pretty(node))==False:
                #n=TGraphNode(self.pretty(node), self.short_info(node))
                #graphnodes[self.pretty(node)] = n
                #n.SetFillColor(self.intcolor(node))
                #n.SetTextSize(0.02)
                #graph.AddNode( graphnodes[self.pretty(node)])
        #for nodeid in nodeids:
            #node = self.history[nodeid]
            #for c in node.parents:
                #edge=TGraphEdge(graphnodes[self.pretty(c)],graphnodes[self.pretty(node)])
                #edge.SetLineStyle(1)
                #graph.AddEdge( edge)
        #for nodeid in nodeids:
            #node = self.history[nodeid]
            #if self.short(node)== 'b':
                #bl=self.object(node)
                #if len(bl.element_uniqueids)>2:
                    #self.graph_add_block_root(graph, graphnodes, bl)
        #pass
    
    #def graph_add_block_root(self,graph, graphnodes, pfblock):
        ##this documents the pfblock linkages in red (need to add distance text for root)
        #from ROOT import TGraphStruct,TGraphNode, TGraphEdge    
    
        #for edge in pfblock.edges.itervalues():
            #if  edge.linked: 
                #edge=TGraphEdge(graphnodes[Identifier.pretty(edge.id1)],graphnodes[Identifier.pretty(edge.id2)])
                #edge.SetLineStyle(2)
                #edge.SetLineColor(2)
                #graph.AddEdge( edge) 
    
        #pass    
                
        
    
    
    
 #experimental stuff eg send to matplotlib, read in and put png file on screen etc   
            #import matplotlib.pyplot as plt
                #import matplotlib.image as mpimg
                #from cStringIO import StringIO
                #from PIL import Image
                #import numpy as np
                #import pylab as pylab
                #import matplotlib.cm as cm        
    
            #graphnodes = {}
    
            #for node in BFS.result:
                #if   graphnodes.has_key(self.pretty(node))==False:
                    #graphnodes[self.pretty(node)] = pydot.Node(self.pretty(node), style="filled", label=self.short_info(node), fillcolor=self.color(node))
                    #graph.add_node( graphnodes[self.pretty(node)])
            #for node in BFS.result:
                    #for c in node.parents:
                        #if len(graph.get_edge(graphnodes[self.pretty(c)],graphnodes[self.pretty(node)]))==0:
                            #graph.add_edge(pydot.Edge(  graphnodes[self.pretty(c)],graphnodes[self.pretty(node)]))
            #for node in BFS.result:
                    #if self.short(node)== 'b':
                        #bl=self.object(node)
                        #if len(bl.element_uniqueids)>2:
                            #self.graph_add_block(graph, graphnodes, bl)                        
    
    
    
            #namestring='plot_dag_' + str(self.pfevent.event.iEv) +'_item_' + Identifier.pretty(id) + '.png'
            #graph.write_png(namestring)  
    
            #if display
            #image=Image.open(namestring)#.show() #to as is rather than in matplot lib window
            # = plt.imshow(np.asarray(image) )       
            #plt.show()        
    
            #png_str = d.create_png()
            #sio = StringIO() # file-like string, appropriate for imread below
            #sio.write(png_str)
            #sio.seek(0)
            #img = mpimg.imread(sio)
    
            #multiplot
            #fig, ax_lst = plt.subplots(2, 2, figsize=(15, 10), sharex='col', sharey='row')
            #fig.tight_layout(pad=0, h_pad=.1, w_pad=.1)
            #for ax in ax_lst.ravel():
                #ax.imshow(img)
            #plt.savefig('foo.png')
    
            #imgplot = plt.imshow(img)        
            #plt.show()
    
    
    
            #original
    
            #image=Image.open(namestring)
    ##another way to read in png files and send to matplotlib        
            #f = pylab.figure()
            #for n, fname in enumerate(('1.png', '2.png')):        
                #arr=np.asarray(image)
            ##f.add_subplot(2, 1, n)  # this line outputs images on top of each other
                #f.add_subplot(1, 2, n)  # this line outputs images side-by-side
                #pylab.imshow(arr)#,cmap=cm.Greys_r)        
                ##pylab.imshow(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))
            #pylab.show()        
    
    
            ##or without quite saving it to file
            #import tempfile
            #fout = tempfile.NamedTemporaryFile(suffix=".png")
            #graph.write(fout.name,format="png")
            #Image.open(fout.name).show()    
            #plt.show()
            #pass
            
            
            
            #nx.draw(nx.graphviz_layout(G))
                #plt.show() 
                #nx.draw(nx.spring_layout(G))
                #plt.show
            
            
                ##import graphViz4Matlab
            
            
                ##import tempfile, Image
                ##fout = tempfile.NamedTemporaryFile(suffix=".png")
                ##gr.write(fout.name,format="png")
                ##Image.open(fout.name).show()        
            
                #from cStringIO import StringIO
            
                #import matplotlib.pyplot as plt
                #import matplotlib.image as mpimg
                #import networkx as nx
            
                ## create a networkx graph
                #G = nx.MultiDiGraph()
                #G.add_nodes_from([1,2] )
                #G.add_edge(1, 2)
            
                ## convert from networkx -> pydot
                #pydot_graph = G.to_pydot()
            
                ## render pydot by calling dot, no file saved to disk
                #png_str = pydot_graph.create_png(prog='dot')
            
                ## treat the dot output string as an image file
                #sio = StringIO()
                #sio.write(png_str)
                #sio.seek(0)
                #img = mpimg.imread(sio)
            
                ## plot the image
                #imgplot = plt.imshow(img, aspect='equal')
                #plt.show(block=False)        
            
            
                #G=nx.complete_graph(5)        
                #nx.networkx_from_pydot(graph)
                #nx.draw(nx.graphviz_layout())
                #plt.show()                 
            
                ##K5=nx.complete_graph(5)
                ##>>> A=nx.to_pydot(K5)
                ##>>> G=nx.from_pydot(A)
                ##>>> G=nx.from_pydot(A,edge_attr=False)               
    
    #def rubbish_networkx_graph_item (self, id,  direction='undirected'):

        #import networkx as nx
        #from networkx.drawing.nx_pydot import to_pydot
        #import matplotlib.pyplot as plt
        #labels=dict()
        #colors=dict()            

        #G=nx.MultiDiGraph()

        #BFS = BreadthFirstSearchIterative(self.history[id], direction) 
        #for node in BFS.result:
            #G.add_node(self.pretty(node),  style="filled",fillcolor=self.color(node),label=self.short_info(node))
            #labels[self.pretty(node)] = self.short_info(node)
            #colors[self.pretty(node)] = self.color(node)                

        #for node in BFS.result:
            #for c in node.parents:
                #G.add_edge(self.pretty(c),self.pretty(node),width=2, weight=1)

        #d = to_pydot(G) # d is a pydot graph object, dot options can be easily set
        #if isinstance(colors, dict):
            #color_lut =  colors 
            #colors = [ color_lut.get(node,'white') for node in G]


        #pos=nx.drawing.nx_pydot.pydot_layout(G, prog='dot')
        #nx.draw(G, pos,font_size=10,fillcolor=colors,node_color=colors, colors=colors,labels=labels, node_size=2000, edge_width=1)        
        #plt.show()
        #pass    