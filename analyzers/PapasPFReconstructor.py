from heppy.framework.analyzer import Analyzer
from heppy.papas.pfalgo.pfreconstructor import PFReconstructor as PFReconstructor
from heppy.papas.data.pfevent import PFEvent
from heppy.papas.pfalgo.distance  import Distance
from heppy.papas.data.history import History

from heppy.display.core import Display
from heppy.display.geometry import GDetector
from heppy.display.pfobjects import GTrajectories


class PapasPFReconstructor(Analyzer):
    ''' Module to reconstruct particles from blocks of events
         
        Usage:
        pfreconstruct = cfg.Analyzer(
            PapasPFReconstructor,
            instance_label = 'papas_PFreconstruction', 
            detector = CMS(),
            input_blocks = 'reconstruction_blocks',
            input_history = 'history_nodes', 
            output_history = 'history_nodes',     
            output_particles_dict = 'particles_dict', 
            output_particles_list = 'particles_list'
        )
        
        input_blocks: Name of the the blocks dict in the event
        history: Name of history_nodes
        output_particles_dict = Name for recosntructed particles (as dict), 
        output_particles_list =  Name for recosntructed particles (as list)
    '''
    
    def __init__(self, *args, **kwargs):
        super(PapasPFReconstructor, self).__init__(*args, **kwargs)  
        self.detector = self.cfg_ana.detector
        self.reconstructed = PFReconstructor(self.detector, self.mainLogger)
        self.blocksname =  self.cfg_ana.input_blocks
        self.historyname = self.cfg_ana.history   
        #self.output_particlesdictname = '_'.join([self.instance_label, self.cfg_ana.output_particles_dict])
        self.output_particleslistname = '_'.join([self.instance_label, self.cfg_ana.output_particles_list])
        #TODO self.is_display = self.cfg_ana.display
        self.is_display = True
        if self.is_display:
            self.init_display()        
    
    def init_display(self):
        self.display = Display(['xy','yz'])
        self.gdetector = GDetector(self.detector)
        self.display.register(self.gdetector, layer=0, clearable=False)
        self.is_display = True
    
                
    def process(self, event):
        ''' Calls the particle reconstruction algorithm and returns the 
           reconstructed paricles and updated history_nodes to the event object
           arguments:
                    event must contain blocks made using BlockBuilder'''
        
        self.reconstructed.reconstruct(event)
        
        #setattr(event, self.historyname, self.reconstructed.history_nodes)
        #setattr(event, self.output_particlesdictname, self.reconstructed.particles)
        setattr(event, "rec_particles", self.reconstructed.particles)
        setattr(event, "blocks", self.reconstructed.blocks)       
        
        
        
        #for particle comparison we want a list of particles (instead of a dict) so that we can sort and compare
        reconstructed_particle_list = sorted( self.reconstructed.particles.values(),
                                                   key = lambda ptc: ptc.e(), reverse=True)
        
        setattr(event, self.output_particleslistname, reconstructed_particle_list)
        
        hist = History(event.history_nodes,PFEvent(event))
        
        #for key, gp in event.gen_stable_particles.iteritems():
            ##(2) What reconstructed particles derive from a given generated particle?
            ##eg generated charged hadron -> reconstructed photon + neutral hadron
        
            #pfall= hist.get_linked_objects(key) 
            #rec_particles =pfall['rec_particles']
            #gen_particles =pfall['gen_particles']
            
            #if len(rec_particles)>1 or len(gen_particles)>1:
                #makestring= " ** "
                #for g in gen_particles:
                    #print g
                    #makestring= makestring + g.shortinfo()  + "   "
                #makestring = makestring+ " -> "
                #for r in rec_particles:
                    #print r
                    #makestring= makestring + r.shortinfo()  + "   "
                #print makestring
                #hist.graph_item(gp.uniqueid)
                #pass
             
                                   
       
                   
        for rp in reconstructed_particle_list:   
            print hist.find_summary_string(rp.uniqueid, "undirected")
    
            linked=hist.get_linked_objects(rp.uniqueid)
            #
            if len(linked['blocks'])>1 or len(linked['blocks'].itervalues().next())>6 :
                hist.graph_item(rp.uniqueid)
                print hist.summary_string(rp.uniqueid,linked["ids"])
            pass
        #for rp in reconstructed_particle_list:
            ##
            ##(1) Given a reconstructed charged hadron, what are the linked:-
                ##smeared ecals/hcals
                ##true ecals/hcals
                ##track
                ##generated/simulated particles
            ##(3) Given a reconstructed particle, what simulated particles did it derive from?     
            #if abs(rp.pdgid())>100 and rp.q() != 0: #charged hadron
                #hist.graph_item(rp.uniqueid)
                
                #pfparents= hist.get_linked_objects(rp.uniqueid,"parents")
                #print "\nReconstructed:"
                #print "   " + rp.__str__()    
                #print "Smeared:"
                #for x in pfparents['gen_particles']  :
                    #print "   " + x.__str__() 
                    
                #print "Direct Gen_particles"
                #for x in pfparents['gen_particles']  :
                    #print "   " + x.__str__()    
                    
                #pfall=hist.get_linked_objects(rp.uniqueid) #undirected #
                #print "All Gen particles:"
                #for x in pfall['gen_particles']  :
                    #print "   " + x.__str__()
                        
                #pass
         
        hist.graph_event(event.history_nodes)
        hist.graph_event_root(event.history_nodes)
        #hist.graph.write_png('plot_dag_event_' + str(hist.pfevent.event.iEv) +'.png')
        if self.is_display  :
            self.display.register( GTrajectories(event.sim_particles.values()),
                                   layer=1)      
               
        pass         