import heppy.framework.config as cfg

from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    gen_particles = 'GenParticle',
    rec_particles = 'RecParticle',
    gen_rec_links = 'ParticleLinks',
    gen_vertices  = 'GenVertex'
)

from heppy.analyzers.PapasFromFccsw import PapasFromFccsw
papas_process = cfg.Analyzer(
    PapasFromFccsw,
    instance_label = 'papas_from_fccsw',
    gen_particles = 'gen_particles',
    rec_particles = 'rec_particles',
    gen_rec_links = 'gen_rec_links',
    verbose = True
)
 