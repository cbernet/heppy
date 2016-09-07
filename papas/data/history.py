from heppy.papas.graphtools.DAG import Node, BreadthFirstSearchIterative
from heppy.papas.data.identifier import Identifier
import pydot
import matplotlib

class History(object):
    '''   
       Object to assist with printing and reconstructing histories
       may need to be merged with pfevent
       only just started ...
    '''    
    def __init__(self, history_nodes, pfevent):
        #this information information needed to be able to unravel information based on a unique identifier
        self.history_nodes = history_nodes
        self.pfevent = pfevent
        
    def find_summary_string(self, rootid, direction="undirected"):
        
        #find everything that is linked to this id
        #and write a summary of what is found
        #the BFS search returns a list of the ids that are  connected to the id of interest
        BFS = BreadthFirstSearchIterative(self.history_nodes[rootid], direction)
        return self.summary_string(rootid, [ v.get_value() for v in BFS.result])    
    
    def summary_string(self, id,  nodeids):
        #print out all the components in the block
        linked=self.get_linked_object_dict(nodeids)
        print "history connected to node:",  self.pfevent.get_object(id).__str__()
        for k in ["gen_particles","gen_tracks","tracks", "ecals", "smeared_ecals","gen_ecals","hcals", 
                  "smeared_hcals","gen_hcals","rec_particles"]:
            newlist = [v.__str__() for a, v in linked[k].items()]
            print k.rjust(13, ' '), '\n              '.join(newlist)
        pass          
        
    def get_linked_objects(self, id, direction="undirected"): #get linked nodes
        BFS = BreadthFirstSearchIterative(self.history_nodes[id], direction)
        linked = self.get_linked_object_dict([v.get_value() for v in BFS.result])
        linked["ids"] = [v.get_value() for v in BFS.result]
        linked['rootid'] = id
        linked['direction'] = direction
        return linked;
    
    def get_linked_object_dict(self, ids): #get object dict
        linked_objects = {}    
        tracks = {}    
        ecals = {}    
        hcals = {}    
        sim_particles = {}
        smeared_ecals = {}
        smeared_hcals = {}
        gen_particles = {}
        gen_tracks = {}
        gen_ecals = {}
        gen_hcals = {}         
        rec_particles = {}
        blocks = {}       
        for id in ids:
            obj = self.pfevent.get_object(id)
            if Identifier.is_block(id):
                blocks[id] = obj            
            elif Identifier.is_track(id):
                if type(obj).__name__ == "Track":
                    gen_tracks[id] = obj  
                if type(obj).__name__ == "SmearedTrack":
                    tracks[id] = obj                   
            elif Identifier.is_ecal(id):
                if type(obj).__name__ == "Cluster":
                    gen_ecals[id] = obj   
                elif type(obj).__name__ == "SmearedCluster":
                    smeared_ecals[id] = obj   
                else:
                    ecals[id] = obj   
            elif Identifier.is_hcal(id):
                if type(obj).__name__ == "Cluster":
                    gen_hcals[id] = obj   
                elif type(obj).__name__ == "SmearedCluster":
                    smeared_hcals[id] = obj    
                else:
                    hcals[id] = obj          
            elif Identifier.is_rec_particle(id):
                rec_particles[id] = obj  
            elif Identifier.is_particle(id):
                gen_particles[id] = obj  
            elif Identifier.is_sim_particle(id):
                sim_particles[id] = obj           
    
        linked_objects["blocks"] = blocks
        linked_objects["tracks"] = tracks
        linked_objects["ecals"] = ecals
        linked_objects["hcals"] = hcals
        linked_objects["sim_particles"] = sim_particles
        linked_objects["smeared_ecals"] = smeared_ecals
        linked_objects["smeared_hcals"] = smeared_hcals
        linked_objects["gen_particles"] = gen_particles
        linked_objects["gen_tracks"] = gen_tracks
        linked_objects["gen_ecals"] = gen_ecals
        linked_objects["gen_hcals"] = gen_hcals
        linked_objects["rec_particles"] = rec_particles
        return  linked_objects   

    def short_name(self, node):
        z = node.get_value()
        return Identifier.pretty(z)
    
    def short(self, node):
        z = node.get_value()
        return Identifier.type_short_code(z) 
        
    def short_info(self, node):
        obj=self.object(node)
        return Identifier.type_short_code(obj.uniqueid) +obj.shortinfo()       
       
    def color(self, node):
        cols =["red", "lightblue", "green", "yellow","cyan", "grey", "white","pink"]
        intcols =[1,2,3,4,5,6,7,8]
        return cols[Identifier.get_type(node.get_value())]            
            
    def intcolor(self, node):
        intcols =[1,2,3,4,5,6,7,8]
        return intcols[Identifier.get_type(node.get_value())]            

    def object(self, node):
        z = node.get_value()
        return self.pfevent.get_object(z) 
              
    def graph_item (self, id,  direction = 'undirected'):
        graph = pydot.Dot(graph_type='digraph')   
        graphnodes = dict()            
        BFS = BreadthFirstSearchIterative(self.history_nodes[id], direction) 
        ids=[]
        for n in BFS.result:
            ids.append(n.get_value())
        self.graph_ids(ids, graph, graphnodes)
        namestring='plot_dag_' + str(self.pfevent.event.iEv) +'_item_' + Identifier.pretty(id) + '.png'
        graph.write_png(namestring) 
    
    def graph_event(self, nodeids): 
        graph = pydot.Dot(graph_type='digraph')
        graphnodes = dict()                
        self.graph_ids(nodeids, graph, graphnodes)
        namestring = 'plot_dag_' + str(self.pfevent.event.iEv)  + '.png'
        graph.write_png(namestring)    
        
    def graph_add_block (self,graph, graphnodes, pfblock):
        intcols =[1,2,3,4,5,6,7,8]
        for edge in pfblock.edges.itervalues():
            if  edge.linked: 
                graph.add_edge(pydot.Edge(  graphnodes[Identifier.pretty(edge.id1)],graphnodes[Identifier.pretty(edge.id2)],
                label=round(edge.distance,1),style="dashed", color="red",arrowhead="none",arrowtail="none",fontsize='7' ))
        pass      
                     
    
        
    def graph_ids (self, nodeids, graph, graphnodes):

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
                    self.graph_add_block(graph, graphnodes, bl)             
             
    def graph_event_root(self, nodeids): 
        from ROOT import TGraphStruct,TGraphNode, TGraphEdge, gPad, TCanvas
        can=TCanvas("History","c",200000,1200)        
        graph = TGraphStruct()
        graphnodes = dict()                
        self.graph_ids_root(nodeids, graph, graphnodes)
        graph.Draw()
        can.Draw()
        gPad.Update()
        pass
    
    def graph_item_root (self, id,  direction='undirected'):
        can=TCanvas("History","c",600,600)       
        graph = TGraphStruct()
        graphnodes = dict()            
        BFS = BreadthFirstSearchIterative(self.history_nodes[id], direction) 
        graphnodes = {}
        ids=[]
        for n in BFS.result:
            ids.append(n.get_value())        
        self.graph_ids_root (ids,graph, graphnodes )
        graph.Draw()
        can.Draw()
        gPad.Update()
        graph.Draw()   
        pass
    
    def graph_ids_root (self, nodeids,graph, graphnodes ):  
        from ROOT import TGraphStruct,TGraphNode, TGraphEdge, gPad, TCanvas
    
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
        from ROOT import TGraphStruct,TGraphNode, TGraphEdge    
    
        for edge in pfblock.edges.itervalues():
            if  edge.linked: 
                edge=TGraphEdge(graphnodes[Identifier.pretty(edge.id1)],graphnodes[Identifier.pretty(edge.id2)])
                edge.SetLineStyle(2)
                edge.SetLineColor(2)
                graph.AddEdge( edge) 
    
        pass    

        
    
    
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
                #if   graphnodes.has_key(self.short_name(node))==False:
                    #graphnodes[self.short_name(node)] = pydot.Node(self.short_name(node), style="filled", label=self.short_info(node), fillcolor=self.color(node))
                    #graph.add_node( graphnodes[self.short_name(node)])
            #for node in BFS.result:
                    #for c in node.parents:
                        #if len(graph.get_edge(graphnodes[self.short_name(c)],graphnodes[self.short_name(node)]))==0:
                            #graph.add_edge(pydot.Edge(  graphnodes[self.short_name(c)],graphnodes[self.short_name(node)]))
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

        #BFS = BreadthFirstSearchIterative(self.history_nodes[id], direction) 
        #for node in BFS.result:
            #G.add_node(self.short_name(node),  style="filled",fillcolor=self.color(node),label=self.short_info(node))
            #labels[self.short_name(node)] = self.short_info(node)
            #colors[self.short_name(node)] = self.color(node)                

        #for node in BFS.result:
            #for c in node.parents:
                #G.add_edge(self.short_name(c),self.short_name(node),width=2, weight=1)

        #d = to_pydot(G) # d is a pydot graph object, dot options can be easily set
        #if isinstance(colors, dict):
            #color_lut =  colors 
            #colors = [ color_lut.get(node,'white') for node in G]


        #pos=nx.drawing.nx_pydot.pydot_layout(G, prog='dot')
        #nx.draw(G, pos,font_size=10,fillcolor=colors,node_color=colors, colors=colors,labels=labels, node_size=2000, edge_width=1)        
        #plt.show()
        #pass    