'''Papas event display'''
from heppy.papas.data.historyhelper import HistoryHelper
from heppy.display.core import Display
from heppy.display.geometry import GDetector
from heppy.display.trajectories import GHistoryBlock
from ROOT import gPad

class EventPlotter(object):

    '''Papas event display.
    '''
      
    def plot(self, papasevent, plottype, nscreens, particles_type_and_subtypes, 
                   clusters_type_and_subtypes, 
                   num_subgroups=None,
                   to_file=False):
        ''' Produces one or more papas event plots depending on options
        
        @param plottype: 'event' - plots all elements in an event
                         'subgroups' - plots are one per subgroup
        @param screennames: List of names for subscreens (also used to decide whether to plot a single event display 
                         or a comparison (two plots side by side)) eg ["simulation", "reconstruction"]
        @param particles_type_and_subtypes: list of particle type_and_subtypes to plot. Length of list must match the length of screennames
                                      eg ['ps', 'pr'] for simulated particles ('ps') on left, reconstructed particles ('pr') on right
        @param clusters_type_and_subtypes: list of lists of  clusters to plot, length of list must be same as the length of screennames
                         eg [['es', 'hs'], ['em', 'hm']] would plot smeared ecals ('es') and smeared hcals ('hs') on left
                             and merged ecals ('em') and merged hcals ('hm') on right
        @param num_subgroups: if specified and if plottype = "subgroups" the biggest n subgroups will be plotted
        @param to_file: if set produces png files of the plots
        '''
    
        
        if len(self.cfg_ana.particles_type_and_subtypes) != self.nscreens or \
           len(self.cfg_ana.clusters_type_and_subtypes) != self.nscreens  or \
           len(self.cfg_ana.self.screennames) == 0 or self.nscreens > 2:
            raise(ValueError, "Input arguments are not consistent for event plot")         

        hhelper = HistoryHelper(papasevent)    
        filename = None        
        if to_file: #sort out the base of the filename
            basename = "event_" + str(self.papasevent.iEv)
            if nscreens == 2:
                basename = "compare_"  + basename          
        
        if plottype == "event":  #full event on one plot
            ids = self.helper.event_ids() 
            if to_file:
                filename = basename + ".png"
            self.plot_ids(ids, particles_type_and_subtypes, 
                               clusters_type_and_subtypes, 
                               filename 
                               )                
        elif plottype == "subgroups": #separate plot per subgroup
            subgraphs = self.helper.get_history_subgroups()        
            if num_subgroups is None: 
                num_subgroups = len(subgraphs) #do all subgroups
            for i in range(num_subgroups):
                if to_file:
                    filename = basename + '_subgroup_' + str(i) + '.png'
                self.plot_ids(subgraphs[i], nscreens, particles_type_and_subtypes, 
                               clusters_type_and_subtypes, 
                               filename 
                               )                           
            
   
    def plot_ids(self, ids, nscreens, particles_type_and_subtypes, 
                 clusters_type_and_subtypes, 
                 filename= None
                 ):
        '''Displays an event plot depending on options, and sends to a file (png) if specified
        @param ids: list of ids to be used on the plot
        @param screennames: List of names for subscreens (also used to decide whether to plot a single event display 
                         or a comparison (two plots side by side)) eg ["simulation", "reconstruction"]
        @param particles_type_and_subtypes: list of particle type_and_subtypes to plot. Length of list must match the length of screennames
                                      eg ['ps', 'pr'] for simulated particles ('ps') on left, reconstructed particles ('pr') on right
        @param clusters_type_and_subtypes: list of lists of  clusters to plot, length of list must be same as the length of screennames
                         eg [['es', 'hs'], ['em', 'hm']] would plot smeared ecals ('es') and smeared hcals ('hs') on left
                             and merged ecals ('em') and merged hcals ('hm') on right
        @param filename: if set prodices png files of the plots
        
        '''
        #collect up the particles and clusters to be plotted
        particles = self.helper.get_collection(ids, particles_type_and_subtypes[0])
        clusters = dict()
        for tp in clusters_type_and_subtypes[0]:
            clusters.update( self.helper.get_collection(ids, tp))
        
        #if comparison particles and clusters are provided thn
        #we will have a screen with two panes and will plot
        #first set of particles (simulation) in colour on left with compare_particles (reconstruction) also in grey
        #and the inverse on the right hand side.
        if nscreens == 2:
            compare = True
            compare_particles = self.helper.get_collection(ids, particles_type_and_subtypes[1])
            compare_clusters = dict()
            for tp in clusters_type_and_subtypes[1]:
                compare_clusters.update(self.helper.get_collection(ids, tp)) 
                
        self.display.clear()     
        #plot main set of particles/clusters on left
        self.display.register( GHistoryBlock(particles, clusters, self.detector, is_grey=False), layer=2, sides=[0])     
        if compare: #add in comparisons in needed
            #NB layer is used to make sure grey is plotted underneath, color on top
            self.display.register( GHistoryBlock(particles, clusters, self.detector, is_grey=True), layer=1, sides=[1])
            self.display.register( GHistoryBlock(compare_particles, compare_clusters, self.detector, is_grey=True), layer=1, sides=[0])
            self.display.register( GHistoryBlock(compare_particles, compare_clusters, self.detector, is_grey=False), layer=2, sides=[1])
        
        self.display.draw()   
        if filename:
            gPad.SaveAs('/'.join([self.directory, filename]))  
            



