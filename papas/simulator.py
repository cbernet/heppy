import sys
import copy
import shelve
from heppy.papas.propagator import propagator
from heppy.papas.pfobjects import Cluster, SmearedCluster, SmearedTrack, Track
from heppy.papas.pfobjects import Particle as PFSimParticle
from heppy.papas.data.papasevent import  PapasEvent
from heppy.utils.pdebug import pdebugger
from heppy.papas.data.identifier import Identifier
import heppy.papas.multiple_scattering as mscat
from heppy.papas.papas_exceptions import SimulationError
from heppy.utils.pdebug import pdebugger
import heppy.statistics.rrandom as random
from heppy.papas.graphtools.DAG import Node


def pfsimparticle(ptc, index):
    '''Create a PFSimParticle from a particle.
    The PFSimParticle will have the same p4, vertex, charge, pdg ID.
    '''
    tp4 = ptc.p4()
    vertex = ptc.start_vertex().position()
    charge = ptc.q()
    pid = ptc.pdgid()
    simptc = PFSimParticle(tp4, vertex, charge, index, pid)
    pdebugger.info(" ".join(("Made", simptc.__str__())))
    simptc.gen_ptc = ptc
    return simptc

class Simulator(object):

    def __init__(self, detector, logger=None):
        self.verbose = True
        self.detector = detector
        if logger is None:
            import logging
            logging.basicConfig(level='ERROR')
            logger = logging.getLogger('Simulator')
        self.logger = logger
        self.reset()   

    def write_ptcs(self, dbname):
        db = shelve.open(dbname)
        db['ptcs'] = self.ptcs
        db.close()

    def reset(self):
        self.ptcs = []
        self.simulated_particles = dict()
        self.smeared_tracks=dict()
        self.smeared_hcals = dict()
        self.true_hcals = dict()
        self.smeared_ecals = dict()
        self.true_ecals = dict()    
        self.smeared_tracks = dict()
        self.true_tracks = dict()   
        self.history = dict()
        Cluster.max_energy = 0.
        SmearedCluster.max_energy = 0.

    def propagate(self, ptc):
        '''propagate the particle to all detector cylinders'''
        propagator(ptc.q()).propagate([ptc], self.detector.cylinders(),
                                      self.detector.elements['field'].magnitude)
        
    def cluster_collection(self, layer):
        if layer == 'ecal_in':
            return self.true_ecals
        elif layer == 'hcal_in':
            return self.true_hcals
        else:
            raise SimulationError("unrecognised layer for a cluster")        
        
    def smeared_cluster_collection(self, layer):
        if layer == 'ecal_in':
            return self.smeared_ecals
        elif layer == 'hcal_in':
            return self.smeared_hcals
        else:
            raise SimulationError("unrecognised layer for a smeared cluster")    

    def make_and_store_cluster(self, ptc, detname, fraction=1., size=None):
        '''adds a cluster in a given detector, with a given fraction of
        the particle energy.
        Stores the cluster in the appropriate collection and records cluster in the history'''
        detector = self.detector.elements[detname]
        propagator(ptc.q()).propagate_one(ptc,
                                          detector.volume.inner,
                                          self.detector.elements['field'].magnitude)
        if size is None:
            size = detector.cluster_size(ptc)
        cylname = detector.volume.inner.name
        if not cylname in ptc.points:
            # TODO Colin particle was not extrapolated here...
            # issue must be solved!
            errormsg = '''
SimulationError : cannot make cluster for particle: 
particle: {ptc}
with vertex rho={rho:5.2f}, z={zed:5.2f}
cannot be extrapolated to : {det}\n'''.format(ptc=ptc,
                                              rho=ptc.vertex.Perp(),
                                              zed=ptc.vertex.Z(),
                                              det=detector.volume.inner)
            self.logger.warning(errormsg)
            raise SimulationError('Particle not extrapolated to the detector, so cannot make a cluster there. No worries for now, problem will be solved :-)')
        clusters = self.cluster_collection(cylname)
        cluster = Cluster(ptc.p4().E()*fraction, ptc.points[cylname], size, cylname, len(clusters), ptc)
        #update collections and history
        ptc.clusters[cylname] = cluster
        clusters[cluster.uniqueid] = cluster 
        self.update_history(ptc.uniqueid, cluster.uniqueid,)          
        pdebugger.info(" ".join(("Made", cluster.__str__())))
        return cluster

    def make_and_store_smeared_cluster(self, cluster, detector, accept=False, acceptance=None):
        '''Returns a copy of self with a smeared energy.
        If accept is False (default), returns None if the smeared
        cluster is not in the detector acceptance. '''
        eres = detector.energy_resolution(cluster.energy, cluster.position.Eta())
        response = detector.energy_response(cluster.energy, cluster.position.Eta())
        energy = cluster.energy * random.gauss(response, eres)
        clusters = self.smeared_cluster_collection(cluster.layer)
        smeared_cluster = SmearedCluster(cluster,
                                         energy,
                                         cluster.position,
                                         cluster.size(),
                                         cluster.layer,
                                         len(clusters),
                                         cluster.particle)
        pdebugger.info(str('Made {}'.format(smeared_cluster)))
        det = acceptance if acceptance else detector
        if det.acceptance(smeared_cluster) or accept:
            clusters[smeared_cluster.uniqueid] = smeared_cluster                      
            self.update_history(cluster.uniqueid, smeared_cluster.uniqueid)            
            return smeared_cluster
        else:
            pdebugger.info(str('Rejected {}'.format(smeared_cluster)))
            return None
    
    def update_history(self, parentid, childid) :
        '''Updates the history adding new nodes if needed and recording parent child relationship'''
        if not self.history.has_key(childid): 
            self.history[childid] = Node(childid)
        if not self.history.has_key( parentid): 
            self.history[ parentid] = Node( parentid)        
        self.history[parentid].add_child(self.history[childid])  

    def make_and_store_track(self, ptc):
        '''creates a new track, adds it into the true_tracks collection and
        updates the history information'''
        track = Track(ptc.p3(), ptc.q(), ptc.path, index=len(self.true_tracks))
        pdebugger.info(" ".join(("Made", track.__str__())))
        self.true_tracks[track.uniqueid] = track                     
        self.update_history(ptc.uniqueid, track.uniqueid)          
        ptc.set_track(track)
        return track
        
    def make_smeared_track(self, track, resolution):
        '''create a new smeared track'''
        #TODO smearing depends on particle type!
        scale_factor = random.gauss(1, resolution)
        smeared_track = SmearedTrack(track,
                                     track.p3 * scale_factor,
                                     track.charge,
                                     track.path,
                                     index = len(self.smeared_tracks))
        pdebugger.info(" ".join(("Made", smeared_track.__str__())))
        return smeared_track  

    def simulate_photon(self, ptc):
        pdebugger.info("Simulating Photon")
        detname = 'ecal'
        ecal = self.detector.elements[detname]
        propagator(ptc.q()).propagate_one(ptc,
                                          ecal.volume.inner)
        cluster = self.make_and_store_cluster(ptc, detname)
        smeared = self.make_and_store_smeared_cluster(cluster,  ecal)
        if smeared:
            ptc.clusters_smeared[smeared.layer] = smeared

    def simulate_neutrino(self, ptc):
        self.propagate(ptc)

    def simulate_hadron(self, ptc):
        '''Simulate a hadron, neutral or charged.
        ptc should behave as pfobjects.Particle.
        '''
        pdebugger.info("Simulating Hadron")
        
        #implement beam pipe scattering
        ecal = self.detector.elements['ecal']
        hcal = self.detector.elements['hcal']
        beampipe = self.detector.elements['beampipe']
        frac_ecal = 0.
        if ptc.q() != 0 :
            #track is now made outside of the particle and then the particle is told where the track is
            track = self.make_and_store_track(ptc)
            resolution = self.detector.elements['tracker'].pt_resolution(track)
            smeared_track = self.make_smeared_track(track, resolution)
            if self.detector.elements['tracker'].acceptance(smeared_track):
                self.smeared_tracks[smeared_track.uniqueid] = smeared_track
                self.update_history(track.uniqueid, smeared_track.uniqueid )   
                ptc.track_smeared = smeared_track 
            else:
                pdebugger.info(str('Rejected {}'.format(smeared_track)))
        
        propagator(ptc.q()).propagate_one(ptc,
                                          beampipe.volume.inner,
                                          self.detector.elements['field'].magnitude)

        propagator(ptc.q()).propagate_one(ptc,
                                          beampipe.volume.outer,
                                          self.detector.elements['field'].magnitude)

        #pdebug next line  must be editted out to match cpp
        #mscat.multiple_scattering(ptc, beampipe, self.detector.elements['field'].magnitude)

        #re-propagate after multiple scattering in the beam pipe
        #indeed, multiple scattering is applied within the beam pipe,
        #so the extrapolation points to the beam pipe entrance and exit
        #change after multiple scattering.
        propagator(ptc.q()).propagate_one(ptc,
                                           beampipe.volume.inner,
                                           self.detector.elements['field'].magnitude)
        propagator(ptc.q()).propagate_one(ptc,
                                           beampipe.volume.outer,
                                           self.detector.elements['field'].magnitude)
        propagator(ptc.q()).propagate_one(ptc,
                                           ecal.volume.inner,
                                           self.detector.elements['field'].magnitude)
        
        if 'ecal_in' in ptc.path.points:
            # doesn't have to be the case (long-lived particles)
            path_length = ecal.material.path_length(ptc)
            if path_length < sys.float_info.max:
                # ecal path length can be infinite in case the ecal
                # has lambda_I = 0 (fully transparent to hadrons)
                time_ecal_inner = ptc.path.time_at_z(ptc.points['ecal_in'].Z())
                deltat = ptc.path.deltat(path_length)
                time_decay = time_ecal_inner + deltat
                point_decay = ptc.path.point_at_time(time_decay)
                ptc.points['ecal_decay'] = point_decay
                if ecal.volume.contains(point_decay):
                    frac_ecal = random.uniform(0., 0.7)
                    cluster = self.make_and_store_cluster(ptc, 'ecal', frac_ecal)
                    # For now, using the hcal resolution and acceptance
                    # for hadronic cluster
                    # in the ECAL. That's not a bug!
                    smeared = self.make_and_store_smeared_cluster(cluster, hcal, acceptance=ecal)
                    if smeared:
                        ptc.clusters_smeared[smeared.layer] = smeared
        cluster = self.make_and_store_cluster(ptc, 'hcal', 1-frac_ecal)
        smeared = self.make_and_store_smeared_cluster(cluster, hcal)
        if smeared:
            ptc.clusters_smeared[smeared.layer] = smeared

    def simulate_electron(self, ptc):
        '''Simulate an electron corresponding to gen particle ptc.
        
        Uses the methods detector.electron_energy_resolution
        and detector.electron_acceptance to smear the electron track.
        Later on, the particle flow algorithm will use the tracks
        coming from an electron to reconstruct electrons.
        
        This method does not simulate an electron energy deposit in the ECAL.
        '''
        pdebugger.info("Simulating Electron")
        ecal = self.detector.elements['ecal']
        track = self.make_and_store_track(ptc)
        propagator(ptc.q()).propagate_one(
            ptc,
            ecal.volume.inner,
            self.detector.elements['field'].magnitude
        )
        eres = self.detector.electron_energy_resolution(ptc)
        smeared_track = self.make_smeared_track(track, eres)
        if self.detector.electron_acceptance(smeared_track):
                self.smeared_tracks[smeared_track.uniqueid] = smeared_track
                self.update_history(track.uniqueid, smeared_track.uniqueid)  
                ptc.track_smeared = smeared_track 
        else:
            pdebugger.info(str('Rejected {}'.format(smeared_track)))
    
    def simulate_muon(self, ptc):
        '''Simulate a muon corresponding to gen particle ptc
        
        Uses the methods detector.muon_energy_resolution
        and detector.muon_acceptance to smear the muon track.
        Later on, the particle flow algorithm will use the tracks
        coming from a muon to reconstruct muons.
        
        This method does not simulate energy deposits in the calorimeters
        '''
        pdebugger.info("Simulating Muon")  
        track = self.make_and_store_track(ptc)
        self.propagate(ptc)
        ptres = self.detector.muon_pt_resolution(ptc)
        smeared_track = self.make_smeared_track(track, ptres)
        if self.detector.muon_acceptance(smeared_track):
            self.smeared_tracks[smeared_track.uniqueid] = smeared_track
            self.update_history(track.uniqueid, smeared_track.uniqueid)    
            ptc.track_smeared = smeared_track 
        else:
            pdebugger.info(str('Rejected {}'.format(smeared_track)))

    def smear_muon(self, ptc):
        pdebugger.info("Smearing Muon")
        self.propagate(ptc)
        if ptc.q() != 0:
            pdebugger.info(" ".join(("Made", ptc.track.__str__())))
        smeared = copy.deepcopy(ptc)
        return smeared

    def smear_electron(self, ptc):
        pdebugger.info("Smearing Electron")
        ecal = self.detector.elements['ecal']
        propagator(ptc.q()).propagate_one(ptc,
                                          ecal.volume.inner,
                                          self.detector.elements['field'].magnitude)
        if ptc.q() != 0:
            pdebugger.info(" ".join(("Made", ptc.track.__str__())))
        smeared = copy.deepcopy(ptc)
        return smeared

    def propagate_muon(self, ptc):
        pdebugger.info("Propogate Muon")
        self.propagate(ptc)
        return

    def propagate_electron(self, ptc):
        pdebugger.info("Propogate Electron")
        ecal = self.detector.elements['ecal']
        propagator(ptc.q()).propagate_one(ptc,
                                          ecal.volume.inner,
                                          self.detector.elements['field'].magnitude)
        return

    def simulate(self, ptcs, history):
        self.reset()
        self.history = history
        # import pdb; pdb.set_trace()
        for gen_ptc in ptcs:
            if gen_ptc.q() and gen_ptc.pt() < 0.2 and abs(gen_ptc.pdgid()) >= 100:
                # to avoid numerical problems in propagation (and avoid making a particle that is not used)
                continue      
            ptc = pfsimparticle(gen_ptc, len(self.simulated_particles))
            self.history[ptc.uniqueid] = Node(ptc.uniqueid)
            if ptc.pdgid() == 22:
                self.simulate_photon(ptc)
            elif abs(ptc.pdgid()) == 11: #check with colin
                # self.propagate_electron(ptc)
                self.simulate_electron(ptc)
            elif abs(ptc.pdgid()) == 13:   #check with colin
                # self.propagate_muon(ptc)
                self.simulate_muon(ptc)
            elif abs(ptc.pdgid()) in [12, 14, 16]:
                self.simulate_neutrino(ptc)
            elif abs(ptc.pdgid()) > 100: #TODO make sure this is ok
                self.simulate_hadron(ptc)
            self.ptcs.append(ptc)
            self.simulated_particles[ptc.uniqueid]= ptc

if __name__ == '__main__':

    import math
    import logging
    from detectors.CMS import cms
    from toyevents import particle
    from heppy.display.core import Display
    from heppy.display.geometry import GDetector
    from heppy.display.pfobjects import GTrajectories

    display_on = True
    detector = cms

    logging.basicConfig(level='WARNING')
    logger = logging.getLogger('Simulator')
    logger.addHandler(logging.StreamHandler(sys.stdout))

    for i in range(1):
        if not i%100:
            print i
        simulator = Simulator(detector, logger)
        # particles = monojet([211, -211, 130, 22, 22, 22], math.pi/2., math.pi/2., 2, 50)
        particles = [
            # particle(211, math.pi/2., math.pi/2., 100),
            particle(211, math.pi/2 + 0.5, 0., 40.),
            # particle(130, math.pi/2., math.pi/2.+0., 100.),
            # particle(22, math.pi/2., math.pi/2.+0.0, 10.)
        ]
        simulator.simulate(particles)

    if display_on:
        display = Display(['xy', 'yz',
                           'ECAL_thetaphi',
                           'HCAL_thetaphi'
                           ])
        gdetector = GDetector(detector)
        display.register(gdetector, 0)
        gtrajectories = GTrajectories(simulator.ptcs)
        display.register(gtrajectories, 1)
        display.draw()

