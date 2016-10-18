from heppy.framework.analyzer import Analyzer
from heppy.papas.pfalgo.pfreconstructor import PFReconstructor as PFReconstructor
from heppy.papas.pfalgo.distance  import Distance
from heppy.papas.data.identifier import Identifier

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
        self.reconstructed = PFReconstructor(self.detector, self.mainLogger) #merge could also be self.logger?
        self.output_particleslistname = '_'.join([self.instance_label, self.cfg_ana.output_particles_list])
        

    def process(self, event):
        ''' Calls the particle reconstruction algorithm and returns the 
           reconstructed paricles and updated history_nodes to the event object
           arguments:
                    event must contain blocks made using BlockBuilder'''
        #should these be passed as analyzer arguments instead?
        ecals = event.papasevent.get_collection('em');
        hcals = event.papasevent.get_collection('hm');
        tracks = event.papasevent.get_collection('ts');
        blocks = event.papasevent.get_collection('br');
        particles = dict()
        splitblocks = dict()

        if blocks:
            self.reconstructed.reconstruct(ecals, hcals , tracks, blocks, event.papasevent)
            particles = self.reconstructed.particles
            splitblocks = self.reconstructed.splitblocks

        event.papasevent.add_collection(particles)
        event.papasevent.add_collection(splitblocks)        
        #for particle comparison we want a list of particles (instead of a dict) so that we can sort and compare

        reconstructed_particle_list = sorted( self.reconstructed.particles.values(),
                                                   key = lambda ptc: ptc.e(),
                                                   reverse=True)
        setattr(event, self.output_particleslistname, reconstructed_particle_list)
            
        Identifier.reset()

