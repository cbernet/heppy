from heppy.framework.analyzer import Analyzer
from heppy.papas.data.papasevent import PapasEvent
from heppy.papas.graphtools.DAG import Node

class PapasEventFromRoot(Analyzer):
    '''Sets up a papas event containing gen and rec particles from a ROOT file (eg using FCCSW papas run output)

    Example configuration:

    from heppy.analyzers.PapasEventFromRoot import PapasEventFromRoot
    papas_from_root = cfg.Analyzer(
        PapasEventFromRoot,
        instance_label = 'papas_from_root',
        gen_particles = 'gen_particles',
        rec_particles = 'rec_particles',
        gen_rec_links = 'gen_rec_links',
        verbose = True
        )
    gen_particles: Name of the input gen particle collection
    rec_particles: Name of the input reconstructed particle collection
    gen_rec_links: Name of the ParticleMcParticleAssociation collection with links between gen and rec particles
    verbose      : Enable the detailed printout.

        event must contain
          gen_particles
          rec_particles
          gen_rec_links
        A papasevent will be created which contains a collection of gen and rec particles and a history that links them
    '''

    def __init__(self, *args, **kwargs):
        super(PapasEventFromRoot, self).__init__(*args, **kwargs)

    def process(self, event):
        event.papasevent = PapasEvent(event.iEv)
        papasevent = event.papasevent
        #make a dict from the gen_particles list so that it can be stored into the papasevent collections
        gen_particles = getattr(event, self.cfg_ana.gen_particles)
        gen_particles_collection = {x.uniqueid():x for x in gen_particles}
        #make a dict from the rec_particles list so that it can be stored into the papasevent collections
        rec_particles = getattr(event, self.cfg_ana.rec_particles)
        rec_particles_collection = {x.uniqueid():x for x in rec_particles}
        #create the history links for relationship between gen and rec particles
        particle_links = getattr(event, self.cfg_ana.gen_rec_links)
        for plink in particle_links:
            nodeid = plink.childid()
            child = papasevent.history.setdefault(nodeid, Node(nodeid)) #creates a new node if it is not there already
            nodeid =  plink.parentid()
            parent = papasevent.history.setdefault(nodeid, Node(nodeid))
            parent.add_child(child)

        papasevent.add_collection(gen_particles_collection)
        papasevent.add_collection(rec_particles_collection)

        #useful when producing outputs from a papasevent
        papasevent.iEv = event.iEv
