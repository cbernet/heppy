import math
import copy
from heppy.papas.data.identifier import Identifier
from heppy.papas.data.historyhelper import HistoryHelper
from heppy.papas.graphtools.edge import Edge
from heppy.papas.graphtools.DAG import Node
from heppy.papas.pfalgo.pfblocksplitter import BlockSplitter
from heppy.papas.pdt import particle_data
from heppy.papas.path import StraightLine, Helix
from heppy.papas.propagator import propagator
from heppy.utils.pdebug import pdebugger
from heppy.papas.pfobjects import Particle
from ROOT import TVector3, TLorentzVector

#Discuss with colin self.locked vs ecal.locked
#209 in reconstruct_block extra ecals to be added in

class PFReconstructor(object):
    ''' The reconstructor takes an event containing blocks of elements
        and attempts to reconstruct particles
        The following strategy is used (to be checked with Colin)
        single elements:
             track -> charged hadron
             hcal  -> neutral hadron
             ecal  -> photon
        connected elements:
              has more than one hcal
                -> each hcal is treated using rules below
              has an hcal with one or more connected tracks
                -> add up all connected track energies, turn each track into a charged hadron
                -> add up all ecal energies connected to the above tracks
                -> if excess = hcal energy + ecal energies - track energies > 0
                       and excess < ecal energies
                           then turn the excess into an photon
                -> if excess > 0 and excess > ecal energies
                          make a neutral hadron with excess- ecal energies
                          make photon with ecal energies
              has hcal but no track (nb by design there will be no attached ecals because hcal ecal links have been removed
                    so this will equate to single hcal:- that two hcals should not occur as a single block
                    because if they are close enough to be linked then they should already have been merged)
                -> make a neutral hadron 
              
              has track(s) 
                -> each track is turned into a charged hadron
              has track(s) and  ecal(s)
                -> the tracks are turned into charged hadrons, the ecals are marked as locked but energy is not checked 
                and no photons are made
                TODO handle case where there is more energy in ecals than in the track and make some photons
              has only ecals 
                -> this should not occur because ecals that are close enough to be linked should already have been merged
        
             
         If history_nodes are provided then the particles are linked into the exisiting history
         
         Contains:
            papasevent: which holds the collections of particle flow elements, blocks , history
            unused: list of unused elements
            particles: list of constructed particles
            splitblocks: the blocks created when the original blocks are simplified and split
            
         Example usage:
         
              reconstructed = PFReconstructor(papasevent, 'br')
              event.reconstructed_particles= sorted( reconstructed.particles,
                            key = lambda ptc: ptc.e(), reverse=True)
        ''' 
    
    def __init__(self, detector, logger):
        self.detector = detector
        self.log = logger

    def reconstruct(self, papasevent, block_type_and_subtype):
        '''papasevent: PapasEvent containing collections of particle flow objects 
           block_type_and_subtype: which blocks collection to use'''
        
        self.unused = []
        self.papasevent = papasevent
        self.history_helper = HistoryHelper(papasevent)
        self.particles = dict()
        self.splitblocks = dict()
        blocks = papasevent.get_collection(block_type_and_subtype)   
        
        # simplify the blocks by editing the links so that each track will end up linked to at most one hcal
        # then recalculate the blocks
        for blockid in sorted(blocks.keys(), reverse=True): #big blocks come first
            pdebugger.info(str('Splitting {}'.format(blocks[blockid])))
            newblocks = self.simplify_blocks(blocks[blockid], self.papasevent.history)
            self.splitblocks.update(newblocks)      
    
        #reconstruct each of the resulting blocks        
        for b in sorted(self.splitblocks.keys(), reverse=True):  #put big interesting blocks first
            sblock = self.splitblocks[b]
            pdebugger.info('Processing {}'.format(sblock))
            self.reconstruct_block(sblock)

        #check if anything is unused
        if len(self.unused):
            self.log.warning(str(self.unused))
        self.log.info("Particles:")
        self.log.info(str(self))         

    def simplify_blocks(self, block, history_nodes=None):
        ''' Block: a block which contains list of element ids and set of edges that connect them
            history_nodes: optional dictionary of Nodes with element identifiers in each node
        
        returns a dictionary of new split blocks
            
        The goal is to remove, if needed, some links from the block so that each track links to 
        at most one hcal within a block. In some cases this may separate a block into smaller
        blocks (splitblocks). The BlockSplitter is used to return the new smaller blocks.
         If history_nodes are provided then the history will be updated. Split blocks will 
         have the tracks and cluster elements as parents, and also the original block as a parent
        '''
        ids = block.element_uniqueids
        #create a copy of the edges and unlink some of these edges if needed
        newedges = copy.deepcopy(block.edges)
        if len(ids) > 1 :   
            for uid in ids :
                if Identifier.is_track(uid):
                    # for tracks unlink all hcals except the closest hcal
                    linked_ids = block.linked_ids(uid, "hcal_track") # NB already sorted from small to large distance
                    if linked_ids != None and len(linked_ids) > 1:
                        first_hcal = True
                        for id2 in linked_ids:
                            newedge = newedges[Edge.make_key(uid, id2)]
                            if first_hcal:
                                first_dist = newedge.distance
                                first_hcal = False
                            else:
                                if newedge.distance == first_dist:
                                    pass 
                                newedge.linked = False 
        #create new block(s)               
        splitblocks = BlockSplitter(block.uniqueid, ids, newedges, len(self.splitblocks), 's', history_nodes).blocks
        return splitblocks
            
    def reconstruct_block(self, block):
        ''' see class description for summary of reconstruction approach
        '''
        uids = block.element_uniqueids #ids are already stored in sorted order inside block
        self.locked = dict( (uid, False) for uid in uids )
        # first reconstruct muons and electrons
        self.reconstruct_muons(block)
        self.reconstruct_electrons(block)
        # keeping only the elements that have not been used so far
        uids = [uid for uid in uids if not self.locked[uid]]
        if len(uids) == 1: #TODO WARNING!!! LOTS OF MISSING CASES
            uid = uids[0]
            parent_ids = [block.uniqueid, uid]
            if Identifier.is_ecal(uid):
                self.reconstruct_cluster(self.papasevent.get_object(uid),
                                         "ecal_in", parent_ids)
            elif Identifier.is_hcal(uid):
                self.reconstruct_cluster(self.papasevent.get_object(uid),
                                         "hcal_in", parent_ids)
            elif Identifier.is_track(uid):
                self.reconstruct_track(self.papasevent.get_object(uid), 211,
                                       parent_ids)
                
        else: #TODO
            for uid in uids: #already sorted to have higher energy things first (see pfblock)
                if Identifier.is_hcal(uid):
                    self.reconstruct_hcal(block, uid)
            for uid in uids: #already sorted to have higher energy things first
                if Identifier.is_track(uid) and not self.locked[uid]:
                # unused tracks, so not linked to HCAL
                # reconstructing charged hadrons.
                # ELECTRONS TO BE DEALT WITH.
                    parent_ids = [block.uniqueid, uid]
                    self.reconstruct_track(self.papasevent.get_object(uid),
                                           211, parent_ids)
                    # tracks possibly linked to ecal->locking cluster
                    for idlink in block.linked_ids(uid, "ecal_track"):
                        #ask colin what happened to possible photons here:
                        self.locked[idlink] = True
                        #TODO add in extra photonsbut decide where they should go?
        self.unused.extend([uid for uid in block.element_uniqueids if not self.locked[uid]])       
       
       
    def is_from_particle(self, unique_id, type_and_subtype, pdgid):
        '''@returns: True if object unique_id comes, directly or indirectly,
        from a particle of type type_and_subtype, with this absolute pdgid. 
        '''
        parents = self.history_helper.get_linked_collection(unique_id,
                                                            type_and_subtype,
                                                            'parents')
        parents_pdgid_filtered = [parent for parent in parents.values()
                                  if abs(parent.pdgid()) == pdgid]
        return bool(len(parents_pdgid_filtered))
       
       
    def reconstruct_muons(self, block):
        '''Reconstruct muons in block.'''
        uids = block.element_uniqueids
        for uid in uids:
            if Identifier.is_track(uid) and \
               self.is_from_particle(uid, 'ps', 13):
                parent_ids = [block.uniqueid, uid]
                self.reconstruct_track(self.papasevent.get_object(uid),
                                       13, parent_ids)
                
       
    def reconstruct_electrons(self, block):
        '''Reconstruct electrons in block.'''
        uids = block.element_uniqueids
        for uid in uids:
            if Identifier.is_track(uid) and \
               self.is_from_particle(uid, 'ps', 11):
                parent_ids = [block.uniqueid, uid]
                track = self.papasevent.get_object(uid)
                ptc = self.reconstruct_track(track,
                                             11, parent_ids)
                # the simulator does not simulate electron energy deposits in ecal.
                # therefore, one should not lock the ecal clusters linked to the
                # electron track as these clusters are coming from other particles.
                
             
    def insert_particle(self, parent_ids, newparticle):
        ''' The new particle will be inserted into the history_nodes (if present).
            A new node for the particle will be created if needed.
            It will have as its parents the block and all the elements of the block.
            '''        
        #Note that although it may be possible to specify more closely that the particle comes from
        #some parts of the block, there are frequently ambiguities and so for now the particle is
        #linked to everything in the block
        if newparticle:
            newid = newparticle.uniqueid
            self.particles[newid] = newparticle            
            #check if history nodes exists
            if self.papasevent.history is None:
                return
            assert(newid not in self.papasevent.history)
            particlenode = Node(newid)  
            self.papasevent.history[newid] = particlenode
            #add in parental history
            for pid in parent_ids:
                self.papasevent.history[pid].add_child(particlenode)

    def neutral_hadron_energy_resolution(self, energy, eta):
        '''Currently returns the hcal resolution of the detector in use.
        That's a generic solution, but CMS is doing the following
        (implementation in commented code)
        http://cmslxr.fnal.gov/source/RecoParticleFlow/PFProducer/src/PFAlgo.cc#3350 
        '''
        resolution = self.detector.elements['hcal'].energy_resolution(energy, eta)
        return resolution
## energy = max(hcal.energy, 1.)
## eta = hcal.position.Eta()
##        stoch, const = 1.02, 0.065
##        if abs(hcal.position.Eta())>1.48:
##            stoch, const = 1.2, 0.028
##        resol = math.sqrt(stoch**2/energy + const**2)
##        return resol

    def nsigma_hcal(self, cluster):
        '''Currently returns 2.
        CMS is doing the following (implementation in commented code)
        http://cmslxr.fnal.gov/source/RecoParticleFlow/PFProducer/src/PFAlgo.cc#3365 
        '''
        return 2
## return 1. + math.exp(-cluster.energy/100.)
    
    def reconstruct_hcal(self, block, hcalid):
        '''
           block: element ids and edges 
           hcalid: uid of the hcal being processed her

           has hcal and has a track
                -> add up all connected tracks, turn each track into a charged hadron
                -> add up all ecal energies
                -> if track energies is greater than hcal energy then turn the missing energies into an ecal (photon)
                      NB this links the photon to the hcal rather than the ecals
                -> if track energies are less than hcal then make a neutral hadron with rest of hcal energy and turn all ecals into photons
              has hcal but no track (nb by design there will be no attached ecals because hcal ecal links have been removed)
                -> make a neutral hadron
              has hcals
                -> each hcal is treated using rules above
        '''
        # hcal used to make ecal_in has a couple of possible issues
        tracks = []
        ecals = []
        hcal = self.papasevent.get_object(hcalid)
        assert (len(block.linked_ids(hcalid, "hcal_hcal")) == 0)  

        trackids = block.linked_ids(hcalid, "hcal_track")
        for trackid in sorted(trackids, reverse = True): #sort by decreasing energy
            tracks.append(self.papasevent.get_object(trackid))
            for ecalid in block.linked_ids(trackid, "ecal_track"):
                # the ecals get all grouped together for all tracks in the block
                # Maybe we want to link ecals to their closest track etc?
                # this might help with history work
                # ask colin.
                if not self.locked[ecalid]:
                    ecals.append(self.papasevent.get_object(ecalid))
                    self.locked[ecalid] = True
                # hcal should be the only remaining linked hcal cluster (closest one)
                #thcals = [th for th in elem.linked if th.layer=='hcal_in']
                #assert(thcals[0]==hcal)
        self.log.info(hcal)
        self.log.info('\tT {tracks}'.format(tracks=tracks))
        self.log.info('\tE {ecals}'.format(ecals=ecals))
        hcal_energy = hcal.energy
        if len(tracks):
            ecal_energy = sum(ecal.energy for ecal in ecals)
            track_energy = sum(track.p3().Mag() for track in tracks)
            for track in tracks:
                #make a charged hadron
                parent_ids = [block.uniqueid, track.uniqueid]  
                linked_ecals = [block.linked_ids(track.uniqueid, "ecal_track")]
                #if len(linked_ecals()>0:
                parent_ids = parent_ids + block.linked_ids(track.uniqueid, "ecal_track") 
                parent_ids = parent_ids + block.linked_ids(track.uniqueid, "hcal_track")
                
                #removed hcal or put in hcal and ecals but only those linked to this track
                self.reconstruct_track(track, 211, parent_ids)

            delta_e_rel = (hcal_energy + ecal_energy) / track_energy - 1.
            # WARNING
            # calo_eres = self.detector.elements['hcal'].energy_resolution(track_energy)
            # calo_eres = self.neutral_hadron_energy_resolution(hcal)
            calo_eres = self.neutral_hadron_energy_resolution(track_energy,
                                                              hcal.position.Eta())
            self.log.info('dE/p, res = {derel}, {res} '.format(
                derel=delta_e_rel,
                res=calo_eres))
            # if False:
            if delta_e_rel > self.nsigma_hcal(hcal) * calo_eres: # approx means hcal energy + ecal energies > track energies
                excess = delta_e_rel * track_energy # energy in excess of track energies
                #print( 'excess = {excess:5.2f}, ecal_E = {ecal_e:5.2f}, diff = {diff:5.2f}'.format(
                #    excess=excess, ecal_e = ecal_energy, diff=excess-ecal_energy))
                if excess <= ecal_energy: # approx means hcal energy > track energies 
                    # Make a photon from the ecal energy
                    # We make only one photon using only the combined ecal energies
                    parent_ids = [block.uniqueid] + [ecal.uniqueid for ecal in ecals]
                    self.reconstruct_cluster(hcal, 'ecal_in', parent_ids, excess)
                    
                else: # approx means that hcal energy>track energies so we must have a neutral hadron
                    #excess-ecal_energy is approximately hcal energy  - track energies
                    parent_ids = [block.uniqueid, hcalid] 
                    self.reconstruct_cluster(hcal, 'hcal_in', parent_ids, 
                                             excess-ecal_energy)
                    if ecal_energy:
                        #make a photon from the remaining ecal energies
                        #again history is confusingbecause hcal is used to provide direction
                        #be better to make several smaller photons one per ecal?
                        parent_ids = [block.uniqueid] + [ecal.uniqueid for ecal in ecals]
                        self.locked[hcal.uniqueid] = False # temp fix by alice
                        self.reconstruct_cluster(hcal, 'ecal_in', parent_ids, ecal_energy)

        else: # case where there are no tracks make a neutral hadron for each hcal
              # note that hcal-ecal links have been removed so hcal should only be linked to 
              # other hcals
            parent_ids = [block.uniqueid, hcalid]     
            self.insert_particle(parent_ids,  self.reconstruct_cluster(hcal, 'hcal_in'))  
        self.locked[hcalid] = True
          
    def reconstruct_cluster(self, cluster, layer, parent_ids,
                            energy=None, vertex=None):
        '''construct a photon if it is an ecal
           construct a neutral hadron if it is an hcal
        '''
        if self.locked[cluster.uniqueid]:
            return 
        if vertex is None:
            vertex = TVector3()
        pdg_id = None
        propagate_to = None
        if layer=='ecal_in':
            pdg_id = 22 #photon
            propagate_to = [ self.detector.elements['ecal'].volume.inner ]
        elif layer=='hcal_in':
            pdg_id = 130 #K0
            propagate_to = [ self.detector.elements['ecal'].volume.inner,
                             self.detector.elements['hcal'].volume.inner ]
        else:
            raise ValueError('layer must be equal to ecal_in or hcal_in')
        assert(pdg_id)
        mass, charge = particle_data[pdg_id]
        if energy is None:
            energy = cluster.energy
        if energy < mass: 
            return None 
        if mass == 0:
            momentum = energy #avoid sqrt for zero mass
        else:
            momentum = math.sqrt(energy**2 - mass**2)
        p3 = cluster.position.Unit() * momentum
        p4 = TLorentzVector(p3.Px(), p3.Py(), p3.Pz(), energy) #mass is not accurate here
        particle = Particle(p4, vertex, charge, len(self.particles), pdg_id, subtype='r')
        # alice: this may be a bit strange because we can make a photon 
        # with a path where the point is actually that of the hcal?
        # nb this only is problem if the cluster and the assigned layer 
        # are different
        propagator(charge).propagate([particle],
                                     propagate_to)
        #merge Nov 10th 2016 not sure about following line (was commented out in papasevent branch)
        particle.clusters[layer] = cluster  # not sure about this either when hcal is used to make an ecal cluster?
        self.locked[cluster.uniqueid] = True #just OK but not nice if hcal used to make ecal.
        pdebugger.info(str('Made {} from {}'.format(particle, cluster)))
        self.insert_particle(parent_ids, particle)        
        
    def reconstruct_track(self, track, pdgid, parent_ids,
                          clusters=None): # cluster argument does not ever seem to be used at present
        '''construct a charged hadron from the track
        '''
        if self.locked[track.uniqueid]:
            return 
        vertex = track.path.points['vertex']
        pdgid = pdgid * track.charge
        mass, charge = particle_data[pdgid]
        p4 = TLorentzVector()
        p4.SetVectM(track.p3() , mass)
        particle = Particle(p4, vertex, charge, len(self.particles), pdgid,  subtype='r')
        #todo fix this so it picks up smeared track points (need to propagagte smeared track)
        particle.set_track(track) #refer to existing track rather than make a new one
        self.locked[track.uniqueid] = True
        pdebugger.info(str('Made {} from {}'.format(particle, track)))
        self.insert_particle(parent_ids, particle)
        return particle

    def __str__(self):
        theStr = ['New Rec Particles:']
        theStr.extend(map(str, self.particles.itervalues()))
        theStr.append('Unused:')
        if len(self.unused) == 0:
            theStr.append('None')
        else:
            theStr.extend(map(str, self.unused))
        return '\n'.join(theStr)
