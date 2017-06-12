from heppy.framework.analyzer import Analyzer
from heppy.papas.pfalgo.pfreconstructor import PFReconstructor as PFReconstructor
from heppy.papas.pfalgo.distance  import Distance
from heppy.papas.data.identifier import Identifier

class PapasPFReconstructor(Analyzer):
    ''' Module to reconstruct particles from blocks of events
         
        from heppy.analyzers.PapasPFReconstructor import PapasPFReconstructor
        pfreconstruct = cfg.Analyzer(
            PapasPFReconstructor,
            track_type_and_subtype = 'ts', 
            ecal_type_and_subtype = 'em', 
            hcal_type_and_subtype = 'hm',
            block_type_and_subtype = 'br',
            instance_label = 'papas_PFreconstruction', 
            detector = detector,
            output_particles_list = 'particles_list'
        )
        
        
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
        ), 
        track_type_and_subtype = which tracks collection in papasevent to use 
        ecal_type_and_subtype = which ecals collection in papasevent to use 
        hcal_type_and_subtype = which hcals collection in papasevent to use 
        block_type_and_subtype = 'which blocks collection in papasevent to use 
        output_particles_list =  Name for reconstructed particles (as list)
    '''
    
    def __init__(self, *args, **kwargs):
        super(PapasPFReconstructor, self).__init__(*args, **kwargs)  

        self.reconstructor = PFReconstructor(self.cfg_ana.detector, self.logger) 
        
##        self.output_particleslistname = '_'.join([self.instance_label,
##                                                  self.cfg_ana.output_particles_list])
        

    def process(self, event):
        ''' Calls the particle reconstruction algorithm and returns the 
           reconstructed paricles and updated history_nodes to the event object
           arguments:
                    event must contain a papasevent which must contain tracks, ecals, hcals and blocks'''
        self.reconstructor.reconstruct( event.papasevent, self.cfg_ana.block_type_and_subtype)
        particles = self.reconstructor.particles
        splitblocks = self.reconstructor.splitblocks
        event.papasevent.add_collection(particles)
        event.papasevent.add_collection(splitblocks)
        #for particle comparison we want a list of particles (instead of a dict) so that we can sort and compare
        reconstructed_particle_list = sorted( particles.values(),
                                              key = lambda ptc: ptc.e(),
                                              reverse=True)
        setattr(event, self.cfg_ana.output, reconstructed_particle_list)


