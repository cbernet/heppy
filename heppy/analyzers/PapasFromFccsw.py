from heppy.framework.analyzer import Analyzer
from heppy.papas.data.papasevent import PapasEvent
from heppy.papas.graphtools.DAG import Node
from heppy.papas.data.idcoder import IdCoder

class PapasFromFccsw(Analyzer):
    '''Sets up a papas event containing gen and rec particles from a ROOT file (eg using FCCSW papas run output)

    Example configuration:

    from heppy.analyzers.PapasFromFccsw import PapasFromFccsw
    papas_from_root = cfg.Analyzer(
        PapasFromFccsw,
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
        super(PapasFromFccsw, self).__init__(*args, **kwargs)

    def process(self, event):
        event.papasevent = PapasEvent(event.iEv)
        papasevent = event.papasevent

        #make a dict from the gen_particles list so that it can be stored into the papasevent collections
        gen_particles = getattr(event, self.cfg_ana.gen_particles)
        gen_particles_collection = {}
        for g in gen_particles:
            #set the papas identifiers for use in DAG
            g.set_dagid(IdCoder.make_id(IdCoder.PFOBJECTTYPE.PARTICLE, g.objid()[0], 'g', g.p4().E()))
            gen_particles_collection[g.dagid()] = g

        #make a dict from the rec_particles list so that it can be stored into the papasevent collections
        rec_particles = getattr(event, self.cfg_ana.rec_particles)

        #if there are no rec_particles we assume this was an evernt discarded during reconstruction and skip it
        if len(rec_particles) == 0:
            self.mainLogger.error('no reconsrtucted particles found -> Event discarded')
            return False
        rec_particles_collection = {}
        for r in rec_particles:
            #set the papas identifiers for use in DAG
            r.set_dagid(IdCoder.make_id(IdCoder.PFOBJECTTYPE.PARTICLE, r.objid()[0], 'r', r.p4().E()))
            rec_particles_collection[r.dagid()] = r

        #create the history links for relationship between gen and rec particles
        particle_links = getattr(event, self.cfg_ana.gen_rec_links)
        for plink in particle_links:
            genid = None
            recid = None
            for g in gen_particles:
                if g.objid() == plink.id1() :
                    genid = g.dagid()
                    break
            for g in rec_particles:
                if g.objid() == plink.id2() :
                    recid = g.dagid()
                    break            
            if recid==None or genid ==None:
                self.mainLogger.error('Error: One of the particles in the Particle Link was not found-> discarding event')
                return False 
            child = papasevent.history.setdefault(recid, Node(recid)) #creates a new node if it is not there already
            parent = papasevent.history.setdefault(genid, Node(genid))
            parent.add_child(child)

        papasevent.add_collection(gen_particles_collection)
        papasevent.add_collection(rec_particles_collection)
