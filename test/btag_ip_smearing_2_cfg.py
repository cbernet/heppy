import heppy.framework.config as cfg
from heppy.configuration import Collider
import math

from heppy.analyzers.ImpactParameterSmearer import ImpactParameterSmearer
def aleph_resolution(ptc):
    momentum = ptc.p3().Mag()
    return math.sqrt(25.**2 + 95.**2/ (momentum**2) )*1e-6

ip_smearer = cfg.Analyzer(
    ImpactParameterSmearer,
    jets = 'jets',
    resolution = aleph_resolution,
 )

btag_ip_smearing = [
    ip_smearer
]
