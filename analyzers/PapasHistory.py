from heppy.framework.analyzer import Analyzer
from heppy.papas.pfalgo.pfreconstructor import PFReconstructor as PFReconstructor
from heppy.papas.data.pfevent import PFEvent
from heppy.papas.pfalgo.distance  import Distance
from heppy.papas.data.history import History

from heppy.display.core import Display
from heppy.display.geometry import GDetector
from heppy.display.pfobjects import GTrajectories, GHistoryBlock

from ROOT import TGraphStruct,TGraphNode, TGraphEdge, gPad, TCanvas
from heppy.papas.data.identifier import Identifier


class PapasHistory(Analyzer):
    ''' Module to handle history? 
        
    '''
    
    def __init__(self, *args, **kwargs):
        super(PapasHistory, self).__init__(*args, **kwargs)  
        self.detector = self.cfg_ana.detector
        
        #TODO self.is_display = self.cfg_ana.display
        self.is_display = True
        if self.is_display:
            self.init_display()        
    
    def init_display(self):
        self.display = Display(['dag','xy','yz'])
        self.gdetector = GDetector(self.detector)
        self.display.register(self.gdetector, layer=0, clearable=False)
        self.is_display = True
    
                
    def process(self, event):
        ''' Produces experimental History outputs for the event (plots or text)'''
        
        #experimental for the timebeing
        
        hist = History(event.history_nodes,PFEvent(event))
        
        #Colin Question2: What reconstructed particles derive from a given generated particle?
        ##eg generated charged hadron -> reconstructed photon + neutral hadron
        
        for key, gp in event.gen_stable_particles.iteritems():
            #everything linked to this particle 
            pfall= hist.get_linked_objects(key) 
            rec_particles =pfall['rec_particles']
            gen_particles =pfall['gen_particles']
            
            if len(rec_particles)>1 or len(gen_particles)>1:
                makestring= " Linked Gen Particles:\n  "
                for g in gen_particles.values():
                    #print g
                    makestring= makestring + g.__str__()  + "\n  "
                for r in rec_particles.values():
                    #print r
                    makestring= makestring + " -> " + r.__str__()  + "\n  "
                print makestring
                #hist.graph_item(gp.uniqueid)
                pass
             
        for rp in event.rec_particles.values():
            # Colins questions
            #(1) Given a reconstructed charged hadron, what are the linked:-
            #smeared ecals/hcals
            #true ecals/hcals
            #track
            #generated/simulated particles
            #(3) Given a reconstructed particle, what simulated particles did it derive from?     
            if abs(rp.pdgid())>100 and rp.q() != 0: #charged hadron
                #access the items which are directly linked to the 
                pfparents= hist.get_linked_objects(rp.uniqueid,"parents")
                print "\nLinked to Reconstructed:"
                print "   " + rp.__str__()    
                print "Smeared Clusters:"
                for x in pfparents['smeared_ecals'].values()  :
                    print "   " + x.__str__() 
                for x in pfparents['smeared_hcals'].values()  :
                    print "   " + x.__str__()                
                print "True Clusters:"
                for x in pfparents['gen_ecals'].values()  :
                    print "   " + x.__str__()    
                print "Smeared Tracks:"
                for x in pfparents['tracks'].values()  :
                    print "   " + x.__str__()                    
                pfall=hist.get_linked_objects(rp.uniqueid) #undirected #
                print "All Gen particles:"
                for x in pfall['gen_particles'].values()  :
                    print "   " + x.__str__()
            pass                                   
            
        #Print/graph what is connected to each rec particle (nb will be overlaps if
        #two rec particles are connected)        
        for rp in event.rec_particles.values():   
            linked=hist.get_linked_objects(rp.uniqueid)
            #just produce outputs for more interesting groups
            if len(linked['blocks'])>1 or len(linked['blocks'].itervalues().next().element_uniqueids)>6 :
                hist.graph_items(linked["ids"])
                print "history connected to node:",  rp.__str__()
                print hist.summary_string_ids(linked["ids"])
            pass
        
        #Go through whole event and Print/graph anything that is more "interesting" 
        subgraphs=hist.get_history_blocks()        
        for s in subgraphs:   
            linked=hist.get_linked_object_dict(s)
            if len(s)>20 : #for example
                hist.graph_items(s) 
                hist.graph_items_root(s) 
                print "Linked History Block \n" + hist.summary_string_ids(linked["ids"])
                pass        
        
        #output graphics        
        if self.is_display  :
            #whole event as DAG
            hist.graph_event(event.history_nodes)
            hist.graph_event(event.history_nodes)
            #display event display for each of the history blocks 
            for s in subgraphs:  
                linked=hist.get_linked_object_dict(s)
                if len(s)>20 : #for example  
                    #not 100% right for these plots yet
                    self.display.register( GHistoryBlock(s, event.simulator.detector, hist, 'rec_particles', False), layer=2) 
                    self.display.register( GHistoryBlock(s, event.simulator.detector, hist, 'sim_particles', True), layer=1) 
                    self.display.draw()        
                    gPad.SaveAs('event_' + str(event.iEv)+ '_item_' + Identifier.pretty(s[0]) + '_rec.png') 
                    self.display.clear()                
            
                    self.display.register( GHistoryBlock(s, event.simulator.detector, hist, 'rec_particles', True), layer=1) 
                    self.display.register( GHistoryBlock(s, event.simulator.detector, hist, 'sim_particles', False), layer=2) 
                    self.display.draw()        
                    gPad.SaveAs('event_' + str(event.iEv) + '_item_' +  Identifier.pretty(s[0]) + '_sim.png') 
                    self.display.clear()                                     
        pass         