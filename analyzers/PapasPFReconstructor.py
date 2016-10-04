from heppy.framework.analyzer import Analyzer
from heppy.papas.pfalgo.pfreconstructor import PFReconstructor as PFReconstructor
from heppy.papas.pfalgo.distance  import Distance



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
        self.output_particleslistname = '_'.join([self.instance_label, self.cfg_ana.output_particles_list])
        
        
    def process(self, event):
        ''' Calls the particle reconstruction algorithm and returns the 
           reconstructed paricles and updated history_nodes to the event object
           arguments:
                    event must contain blocks made using BlockBuilder'''
        
        #todo pass these are argument
        
        ecals = event.papasevent.get_collection('me');
        hcals = event.papasevent.get_collection('mh');
        tracks = event.papasevent.get_collection('st');
        blocks = event.papasevent.get_collection('rb');
        
        self.reconstructed.reconstruct(ecals, hcals , tracks, blocks, event.papasevent)
        
        event.papasevent.add_collection(self.reconstructed.particles)
        event.papasevent.add_collection(self.reconstructed.splitblocks)
        
        
        #setattr(event.papasevent, "rec_particles", self.reconstructed.particles)
        #for particle comparison we want a list of particles (instead of a dict) so that we can sort and compare
        reconstructed_particle_list = sorted( self.reconstructed.particles.values(),
                                                   key = lambda ptc: ptc.uniqueid )
        setattr(event, self.output_particleslistname, reconstructed_particle_list)

