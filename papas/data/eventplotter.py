from heppy.papas.data.identifier import Identifier
import pydot
from heppy.papas.pfalgo.historyhelper import HistoryHelper
from subprocess import call
from heppy.display.core import Display
from heppy.display.geometry import GDetector
from heppy.display.trajectories import GHistoryBlock
from ROOT import gPad

class EventPlotter(object):
    '''   
           Object to assist with plotting event diagrams
          
           Usage:
           eventplot = EventPlotter(papapasevent, detector)
           eventplot.plot_event_compare() #plot normal papas event diagram
           

        '''        
    def __init__(self, papasevent, detector, projections, directory):
        '''
        * papasevent is a PapasEvent
        * detector
        '''
        self.history = papasevent.history
        self.papasevent = papasevent  
        self.helper = HistoryHelper(papasevent)
        self.detector = detector  
        if projections is None:
            projections = ['xy', 'yz']
        self.projections = projections
        self.initialized = False 
        self.directory = directory

    def init_display(self):
        #double paned Display
        #make this a choice via parameters somehow
        if not self.initialized:      
            self.display = Display(self.projections, pads=["simulated", "reconstructed"])
            self.gdetector = GDetector(self.detector)
            self.display.register(self.gdetector, layer=0, clearable=False)  
            self.initialized = True 
        
    def pretty(self, node):
        ''' pretty form of the unique identifier'''
        return Identifier.pretty(node.get_value())
    
    def type_and_subtype(self, node):
        ''' For example 'pg', 'ht' etc'''
        return Identifier.type_and_subtype(node.get_value()) 
                           

    def object(self, node):
        '''returns object corresponding to a node'''
        z = node.get_value()
        return self.papasevent.get_object(z) 

    def plot_event(self):
        '''Event plot containing Simulated particles and smeared clusters 
        '''
        #whole event 
        particles = self.papasevent.get_collection('ps')
        ecals = self.papasevent.get_collection('es')
        hcals = self.papasevent.get_collection('hs')             
        self.display.clear()  
        self.display.register( GHistoryBlock(particles, ecals, hcals, self.detector,  is_grey = False), layer=1, sides = [0])            
        self.display.draw()       
        #gPad.SaveAs('graphs/event_' + str(event.iEv) + '_sim.png')  

    def plot_event_compare(self, to_file = False):
        '''Double event plot for full event
            containing Simulated particles and smeared clusters on left
            and reconstructed particles and merged clusters on right side
            '''    
        self.init_display()      
        self._plot_ids_compare(self.helper.event_ids())             
        self.display.draw() 
        if to_file:
            filename = "event_" + str(self.papasevent.iEv) + '_sim_rec.png'
            gPad.SaveAs('/'.join([self.directory, filename]))   

    def plot_event_subgroups_compare(self, to_file = False, num_subgroups = None):
        '''produces event sub plots of event subgroups (one per subgroup)
           If num_subgroups is specified then the num_subgroups n largest subgroups are plotted
           otherwise all subgroups are plotted
        '''
        subgraphs=self.helper.get_history_subgroups()  
        self.init_display()     
        if num_subgroups is None:
            num_subgroups = len(subgraphs)
        for i in range(num_subgroups): 
            self.plot_event_ids_compare(subgraphs[i], to_file)      
        
    def plot_event_ids_compare(self, ids, to_file = True):
        '''Double event plot for a subgroup of an event
                containing Simulated particles and smeared clusters on left
                and reconstructed particles and merged clusters on right side
                    '''          
        self.display.clear()       
        self._plot_ids_compare(ids)
        self.display.draw() 
        if to_file:
            filename = "event_" + str(self.papasevent.iEv) + '_item_' + Identifier.pretty(ids[0]) + '_sim_rec.png'
            gPad.SaveAs('/'.join([self.directory, filename]))               
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
        self._add_particles(rec_particles, rec_ecals, rec_hcals, position= 0 + offset*2, is_grey = True, layer = 1)
        self._add_particles(rec_particles, rec_ecals, rec_hcals, position= 1 + offset*2, is_grey = False, layer = 2)  
        self._add_particles(sim_particles, sim_ecals, sim_hcals, position= 1 + offset*2, is_grey = True, layer = 1)
    
        
    def _add_particles(self, particles, ecals, hcals, position, is_grey=False , layer = 1):
        self.display.register( GHistoryBlock(particles, ecals, hcals, self.detector,  is_grey), layer=layer, sides = [position]) 
         
    def plot_subevents_panel_compare(self):
        ''' An experiment to plot largest 8 subgroups in an event all at once'''
        
        self.display.clear() 
        subgraphs=self.helper.get_history_subgroups()  
        from itertools import product
        subgraphs.sort(key = lambda s: -len(s))
        ids = []
        for i in range(0, 8):
            ids.append( Identifier.pretty(subgraphs[i][0]))
        lists = [ ids ,["simulated", "reconstructed"]]
        result = ['_'.join(map(str,x)) for x in product(*lists)]   
        self.display = Display(self.projections, pads=result)
        self.display.register(self.gdetector, layer=0, clearable=False)             
        
        for i in range(0, 8):     
            s = subgraphs[i]
            self._plot_ids_compare(s, offset = i)      
        self.display.draw()         
        #gPad.SaveAs('graphs/event_' + str(self.event.iEv) + '_item_' + Identifier.pretty(s[0]) + '_sim_rec_compare.png') 
                             

