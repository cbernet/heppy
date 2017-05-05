import sys
import copy
import shelve
from heppy.papas.propagator import propagator
from heppy.papas.pfobjects import Cluster, SmearedCluster, SmearedTrack, Track
from heppy.papas.data.papasevent import  PapasEvent
from heppy.papas.data.identifier import Identifier
import heppy.papas.multiple_scattering as mscat
from heppy.papas.papas_exceptions import SimulationError
from heppy.utils.pdebug import pdebugger
import heppy.statistics.rrandom as random
from heppy.papas.graphtools.DAG import Node


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

    def reset(self):
        '''Reset the simulator (clears all collections). To be called at each event.
        '''
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
        
    def cluster_collection(self, layer, smeared):
        '''returns the correct cluster collection depending on the layer,
        and whether the true or smeared collection is requested.
        
        @param layer: either "ecal_in" or "hcal_in".
        @param smeared: boolean - if True, the smeared collection is returned.
         otherwise, the unsmeared collection
        '''
        if layer == 'ecal_in':
            if smeared:
                return self.smeared_ecals
            else:
                return self.true_ecals
        elif layer == 'hcal_in':
            if smeared:
                return self.smeared_hcals
            else:
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
        clusters = self.cluster_collection(cylname, smeared=False)
        cluster = Cluster(ptc.p4().E()*fraction, ptc.points[cylname], size, cylname, len(clusters), ptc)
        #update collections and history
        ptc.clusters[cylname] = cluster
        clusters[cluster.uniqueid] = cluster 
        self.update_history(ptc.uniqueid, cluster.uniqueid,)          
        pdebugger.info(" ".join(("Made", cluster.__str__())))
        return cluster

    def make_and_store_smeared_cluster(self, cluster, detector, accept=False, acceptance=None):
        '''Returns a copy of cluster, after a gaussian smearing of the energy.
        
        The smeared cluster is stored for further processing.
        
        @param cluster: the cluster to be smeared.
        @param detector: detector object from which the energy resolution, energy response
          and acceptance parametrizations are taken.
        @param accept: if set to true, always accept the cluster after smearing
        @param acceptance: optional detedctor object for acceptance.
          if provided, and if accept is False, used in place of detector.acceptance
        '''
        eres = detector.energy_resolution(cluster.energy, cluster.position.Eta())
        response = detector.energy_response(cluster.energy, cluster.position.Eta())
        energy = cluster.energy * random.gauss(response, eres)
        clusters = self.cluster_collection(cluster.layer, smeared=True)
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
        child = self.history.setdefault(childid, Node(childid)) #creates a new node if it is not there already
        parent = self.history.setdefault(parentid, Node(parentid))
        parent.add_child(child)   

    def make_and_store_track(self, ptc):
        '''creates a new track, adds it into the true_tracks collection and
        updates the history information'''
        track = Track(ptc.p3(), ptc.q(), ptc.path, index=len(self.true_tracks))
        pdebugger.info(" ".join(("Made", track.__str__())))
        self.true_tracks[track.uniqueid] = track                     
        self.update_history(ptc.uniqueid, track.uniqueid)          
        ptc.set_track(track)
        return track
        
    def make_and_store_smeared_track(self, ptc, track,
                                     detector_resolution, detector_acceptance):
        '''create a new smeared track'''
        #TODO smearing depends on particle type!
        resolution = detector_resolution(ptc)
        scale_factor = random.gauss(1, resolution)
        smeared_track = SmearedTrack(track,
                                     track._p3 * scale_factor,
                                     track.charge,
                                     track.path,
                                     index = len(self.smeared_tracks))
        pdebugger.info(" ".join(("Made", smeared_track.__str__())))
        if detector_acceptance(smeared_track):
            self.smeared_tracks[smeared_track.uniqueid] = smeared_track
            self.update_history(track.uniqueid, smeared_track.uniqueid )   
            ptc.track_smeared = smeared_track             
            return smeared_track  
        else:
            pdebugger.info(str('Rejected {}'.format(smeared_track)))
            return None

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
        frac_ecal = 0.
        if ptc.q() != 0 :
            #track is now made outside of the particle and then the particle is told where the track is
            track = self.make_and_store_track(ptc)
            tracker = self.detector.elements['tracker']
            smeared_track = self.make_and_store_smeared_track(
                ptc, 
                track, 
                tracker.resolution,
                tracker.acceptance
            )
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
        smeared_track = self.make_and_store_smeared_track(
            ptc, track,
            self.detector.electron_resolution,
            self.detector.electron_acceptance
        )

    
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
        smeared_track = self.make_and_store_smeared_track(
            ptc, track,
            self.detector.muon_resolution,
            self.detector.muon_acceptance
        )

    def simulate(self, ptcs, history):
        self.reset()
        self.history = history
        # import pdb; pdb.set_trace()
        for ptc in ptcs:
            if ptc.q() and ptc.pt() < 0.2 and abs(ptc.pdgid()) >= 100:
                # to avoid numerical problems in propagation (and avoid making a particle that is not used)
                continue
            pdebugger.info(str('Simulating {}'.format(ptc)))
            # ptc = pfsimparticle(gen_ptc, len(self.simulated_particles))
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

