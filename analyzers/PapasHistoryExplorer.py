from heppy.framework.analyzer import Analyzer
from heppy.papas.pfalgo.pfreconstructor import PFReconstructor as PFReconstructor
from heppy.papas.pfalgo.distance  import Distance
from heppy.papas.data.historyhelper import HistoryHelper, HistoryPlotHelper

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
        self.is_display = self.cfg_ana.is_display
        self.is_printout = self.cfg_ana.is_printout
        self.dag = self.cfg_ana.dag
        self.top = self.cfg_ana.top
        if self.is_display:
            self.init_display()        
    
    def init_display(self):
        self.display = Display(['dag','xy','yz'], pads=("simulated", "reconstructed"))
        
        #self.display = Display(['dag','xy','yz'])
        self.gdetector = GDetector(self.detector)
        self.display.register(self.gdetector, layer=0, clearable=False)
        self.is_display = True
    
                
    def process(self, event):
        ''' Produces experimental History outputs for the event (plots or text)'''
        
        #experimental for the time being
        self.papasevent = event.papasevent
        self.event= event
        self.hist = HistoryHelper(event.papasevent)
        self.histplot = HistoryPlotHelper(event.papasevent)
        
        if self.is_printout:
            print self.hist.summary_string()
            print self.subgroup_string(top=self.top)
        
        #self.examples()
        if self.is_display:
            self.plot_event_compare()
            if self.dag:
                self.plot_dag_event(show=self.is_display)        
                self.plot_dag_subgroups(top=self.top , show=self.is_display) 
        

        #self.plot_subevents_compare()
        pass
        
    def examples(self) :
    # Colins questions
    #(1) Given a reconstructed charged hadron, what are the linked:-
    #           smeared ecals/hcals/tracks etc
    #(2) What reconstructed particles derive from a given generated particle?
    #
    #(3) Given a reconstructed particle, what simulated particles did it derive from?          
        #eg generated charged hadron -> reconstructed photon + neutral hadron
    
        #question 2
        for id, gp in self.papasevent.get_collection('gp').iteritems():
            all_linked_ids = self.hist.get_linked_ids(id) 
            rec_particles = self.hist.get_matched_collection(all_linked_ids, 'rp')
            gen_particles = self.hist.get_matched_collection(all_linked_ids, 'gp') #linked gen particles
            print self.hist.summary_string_ids(all_linked_ids)
    
        #questions 1  & 3
        for rp in self.event.papasevent.get_collection('rp').values():
            if abs(rp.pdgid())>100 and rp.q() != 0: #charged hadron
                parent_ids= self.hist.get_linked_ids(rp.uniqueid,"parents")
                smeared_ecals = self.hist.get_matched_collection(parent_ids, 'se') 
                #alternatively
                sim_particles = self.hist.get_matched_linked_collection(rp.uniqueid,'sp')
    
            pass                    
    
    
    
    def plot_dag_event(self, show = True):
        if self.is_display  :
            #whole event as DAG
            history=self.papasevent.history
            histplot = HistoryPlotHelper(self.event.papasevent)
            histplot.graph_event(history, show) 
        
    def subgroup_string(self, top = None):
        #Go through whole event and Print anything that is more "interesting" 
        subgraphs=self.hist.get_history_subgroups()  
        result= "Subgroups: \n"
        if top is None:
            top = len(subgraphs)
        for i in range(top):   
            result = result +  "SubGroup " + str(i) +"\n" + self.hist.summary_string_ids(subgraphs[i])
        return result
            
    def plot_dag_subgroups(self, top = None, show = False):
        if self.is_display  :
            subgraphs=self.hist.get_history_subgroups()  
            if top is None:
                top = len(subgraphs)
            for i in range(top):   
                self.histplot.graph_items(subgraphs[i], show)   
 
    def plot_event(self):
        if self.is_display  :
            #whole event as DAG
            history=self.papasevent.history
            sim_particles = self.papasevent.get_collection('sp')
            self.display.clear()  
            self.display.register( GHistoryBlock(history, self.event.detector, hist, sim_particles, False), layer=2) 
            self.display.draw()       
            gPad.SaveAs('graphs/event_' + str(event.iEv) + '_sim.png')  

    def plot_event_compare(self):
        if self.is_display  :
            self.display.clear()       
            self.plot_ids_compare(self.hist.ids())             
            self.display.draw() 
            pass  
        
    def plot_subgroup_compare(self, ids):
        if self.is_display  :
            self.display.clear()       
            self.plot_ids_compare(ids)
            self.display.draw() 
            pass   
        
    def plot_ids_compare(self, ids, offset = 0):
        #reconstructed on right half
        sim_particles = self.hist.get_matched_collection(ids, 'sp')
        rec_particles = self.hist.get_matched_collection(ids,'rp')
        sim_ecals = self.hist.get_matched_collection(ids,'se')
        sim_hcals = self.hist.get_matched_collection(ids,'sh') 
        rec_ecals = self.hist.get_matched_collection(ids,'me')
        rec_hcals = self.hist.get_matched_collection(ids,'mh')             
        self.add_particles(sim_particles, sim_ecals, sim_hcals, position= 0 + offset*2, is_grey = False, layer = 2)
        self.add_particles(sim_particles, sim_ecals, sim_hcals, position= 1 + offset*2, is_grey = True, layer = 1)
        self.add_particles(rec_particles, rec_ecals, rec_hcals, position= 0 + offset*2, is_grey = True, layer = 1)
        self.add_particles(rec_particles, rec_ecals, rec_hcals, position= 1 + offset*2, is_grey = False, layer = 2)   
    
        
    def add_particles(self, particles, ecals, hcals, position, is_grey=False , layer = 1):
        self.display.register( GHistoryBlock(particles, ecals, hcals, self.event.detector,  is_grey), layer=layer, sides = [position]) 
         
    def plot_subevents_compare(self):
        if self.is_display:
            self.display.clear() 
            
            
            subgraphs=self.hist.get_history_subgroups()  
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
            
                       
            #tofo sort by length
            for i in range(0, 8):     
                s = subgraphs[i]
                sim_particles = self.hist.get_matched_collection(s, 'sp')
                rec_particles = self.hist.get_matched_collection(s, 'rp')  
                sim_ecals = self.hist.get_matched_collection(s, 'se')
                rec_ecals = self.hist.get_matched_collection(s, 'me')
                sim_hcals = self.hist.get_matched_collection(s, 'sh')
                rec_hcals = self.hist.get_matched_collection(s, 'mh')                
                
                self.add_particles(sim_particles, sim_ecals, sim_hcals, position= 0 + i*2, is_grey = False, layer = 2)
                self.add_particles(sim_particles, sim_ecals, sim_hcals, position= 1 + i*2, is_grey = True, layer = 1)
                self.add_particles(rec_particles, rec_ecals, rec_hcals, position= 0 + i*2, is_grey = True, layer = 1)
                self.add_particles(rec_particles, rec_ecals, rec_hcals, position= 1 + i*2, is_grey = False, layer = 2)          
        self.display.draw()         
        gPad.SaveAs('graphs/event_' + str(self.event.iEv) + '_sim_rec_compare.png') 
                      