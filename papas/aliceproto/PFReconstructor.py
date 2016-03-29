from heppy.papas.aliceproto.identifier import Identifier
from heppy.papas.aliceproto.DAG import Node
from heppy.papas.aliceproto.BlockSplitter import BlockSplitter
from heppy.papas.pdt import particle_data
from heppy.papas.path import StraightLine, Helix
from heppy.papas.pfobjects import Reconstructed_Particle

from ROOT import TVector3, TLorentzVector
import math
import pprint

#AJRTODO 
#look at mergign
#Tidy / document code and commit it


class PFReconstructor(object):
    ''' The reconstructor takes an event containing blocks of elements
        and attempts to reconstruct particles
        The following strategy is used (to be checked with Colin)
        single elements:
             track -> charged hadron
             hcal  -> neutral hadron
             ecal  -> photon
        connected elements:
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
                    so this will equate to single element about. Note that two hcals should not occur as a single block
                    because if they are close enough to be linked then they should already have been merged)
                -> make a neutral hadron 
              has more than one hcal
                -> each hcal is treated using rules above
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
            blocks: the dictionary of blovks to be reconstructed { blockid; block }
            unused: list of unused elements
            particles: list of constructed particles
            history_nodes: optional, desribes links between elements, blocks, particles
         Example usage:
         
              reconstructed = PFReconstructor(event)
              event.reconstructed_particles= sorted( reconstructed.particles,
                            key = lambda ptc: ptc.e(), reverse=True)
              event.history_nodes=reconstructed.history_nodes
        ''' 
    
    def __init__(self,event): # not sure about if this is the best choice of argument
        '''arguments
              event: should contain blocks and optionally history_nodes'''
        
        self.blocks=event.blocks
        self.unused = []
        self.particles = dict()
        
        # history nodes will be used to connect reconstructed particles into the history
        # its optional at the moment
        if hasattr(event, "history_nodes") :
            self.history_nodes = event.history_nodes
        else : 
            self.history_nodes = None
        
        # simplify the blocks by editing the links so that each track will end up linked to at most one hcal
        # then recalculate the blocks
        splitblocks=dict() 
        #ask colin if there is neater way
        #sort blocks (1) by number of elements (2) by mix of ecal, hcal , tracks (the shortname will look like "H1T2" for a block
        #with one cluster and two tracks)
        for block in sorted(self.blocks, key=lambda k: (len(self.blocks[k].element_uniqueids), self.blocks[k].short_name()),reverse =True):   
            newblocks=self.simplified_blocks(self.blocks[block],event.history_nodes)
            if newblocks != None:
                splitblocks.update( newblocks)
        if len(splitblocks):
            self.blocks.update(splitblocks)
            
        #reconstruct each of the resulting blocks        
        for b in sorted(self.blocks, key=lambda k: (len(self.blocks[k].element_uniqueids), self.blocks[k].short_name()),reverse =True):    
            block=self.blocks[b] #must be slicker way (ask Colin)
            if block.is_active: # when blocks are split the original gets deactivated                
                newparticles=self.reconstruct_block(block)                
                self.insert_particle_history(block,newparticles)                
                #print block, "makes particles"
                #for p in newparticles.itervalues():
                    #print p
                self.particles.update(newparticles)

                self.unused.extend( [id for id in block.element_uniqueids if not self.locked[id]])
                
        #check if anything is unused
        if len(self.unused) :
            print "UNUSED", self.unused
            
        #print(str(self))        
        
 
            
    def simplified_blocks(self, block,history_nodes=None):
        
        ''' Block: a block which contains list of element ids and set of edges that connect them
            history_nodes: optional dictionary of Nodes with element identifiers in each node
        
        returns None or a dictionary of new split blocks
            
        The goal is to remove, if needed, some links from the block so that each track links to 
        at most one hcal within a block. In some cases this may separate a block into smaller
        blocks (splitblocks). The BlockSplitter is used to return the new smaller blocks.
         If history_nodes are provided then the history will be updated. Split blocks will 
         have the tracks and cluster elements as parents, and also the original block as a parent
        '''
        
        ids=block.element_uniqueids
        
        
        if len(ids)<=1 : # no links to remove
            return  None #no split blocks
        
        # work out any links that need to be removed        
        to_unlink = []        
        for id in ids :
            if Identifier.is_track(id) :
                linked = block.linked_edges(id,"hcal_track") # NB already sorted from small to large distance
                if linked!=None :
                    first_hcal = True
                    for elem in linked:
                        if first_hcal:
                            first_hcal = False
                        else:
                            to_unlink.append(elem)
            elif Identifier.is_ecal(id) :
                # this is now handled  and so could be removed
                # remove all ecal-hcal links. ecal linked to hcal give rise to a photon anyway.
                linked = block.linked_edges(id,"ecal_hcal")
                to_unlink.extend(linked)
        
        #if there is something to unlink then use the BlockSplitter        
        splitblocks=None        
        if len(to_unlink) :
            splitblocks= BlockSplitter(block,to_unlink,history_nodes).blocks
        
        return splitblocks
            
    def reconstruct_block(self, block):
        ''' see class description for summary of reconstruction approach
        '''
        particles = dict()
        ids=block.element_uniqueids
        self.locked=dict()
        for id in ids:
            self.locked[id] = False
        
       
        if len(ids)==1: #TODO WARNING!!! LOTS OF MISSING CASES
            id = ids[0]
            
            if Identifier.is_ecal(id) :
                newparticle =self.reconstruct_cluster(block.pfevent.ecal_clusters[id],"ecal_in")
                particles[newparticle.uniqueid]=newparticle
            elif Identifier.is_hcal(id) :
                newparticle =self.reconstruct_cluster(block.pfevent.hcal_clusters[id],"hcal_in")
                particles[newparticle.uniqueid]=newparticle
            elif Identifier.is_track(id) :
                newparticle =self.reconstruct_track(block.pfevent.tracks[id])
                particles[newparticle.uniqueid]=newparticle# ask Colin about energy balance - what happened to the associated clusters that one would expect?
        else: #TODO
            for id in ids :
                if Identifier.is_hcal(id) :
                    
                    particles.update(self.reconstruct_hcal(block,id))
            for id in ids :
                if Identifier.is_track(id) and not self.locked[id] :
                # unused tracks, so not linked to HCAL
                # reconstructing charged hadrons.
                # ELECTRONS TO BE DEALT WITH.
                    newparticle=self.reconstruct_track(block.pfevent.tracks[id])
                    particles[newparticle.uniqueid]=newparticle
                    # tracks possibly linked to ecal->locking cluster
                    for idlink in block.linked_ids(id,"ecal_track") :
                        #ask colin what happened to possible photons here:
                        self.locked[idlink] = True
                        
            # #TODO deal with ecal-ecal
            # ecals = [elem for elem in group if elem.layer=='ecal_in'
            #          and not elem.locked]
            # for ecal in ecals:
            #     linked_layers = [linked.layer for linked in ecal.linked]
            #     # assert('tracker' not in linked_layers) #TODO electrons
            #     self.log.warning( 'DEAL WITH ELECTRONS!' ) 
            #     particles.append(self.reconstruct_cluster(ecal, 'ecal_in'))
            #TODO deal with track-ecal
        return particles 
    
    def insert_particle_history(self, block, particles):
        ''' The new particle will be inserted into the history_nodes (if present).
            A new nodefor the particle will be created if needed.
            It will have as its parents the block and all the elements of the block.
            '''        
        #Note that although it may be possible to specify more closely that the particle comes from
        #some parts of the block, there are frequently ambiguities and so for now the particle is
        #linked to everything in the block
        
        #check if history nodes exists
        if (self.history_nodes == None) :
            return
        
        #find the node for the block        
        blocknode = Node(block.uniqueid)
        
        for particle in particles:
            #find or make a node for the particle            
            if particle  in self.history_nodes :
                pnode = self.history_nodes[particle]
            else :
                pnode = Node(particle)
                self.history_nodes[particle] = pnode
            
            #link particles to the block            
            blocknode.add_child(pnode)
            #link particles to block elements
            for element_id in block.element_uniqueids:
                self.history_nodes[element_id].add_child(pnode)
       
    

    def neutral_hadron_energy_resolution(self, hcal):
        '''WARNING CMS SPECIFIC! 

        http://cmslxr.fnal.gov/source/RecoParticleFlow/PFProducer/src/PFAlgo.cc#3350 
        '''
        energy = max(hcal.energy, 1.)
        stoch, const = 1.02, 0.065
        if abs(hcal.position.Eta())>1.48:
            stoch, const = 1.2, 0.028
        resol = math.sqrt(stoch**2/energy + const**2)
        return resol

    def nsigma_hcal(self, cluster):
        '''WARNING CMS SPECIFIC! 
        
        http://cmslxr.fnal.gov/source/RecoParticleFlow/PFProducer/src/PFAlgo.cc#3365 
        '''
        
        return 1. + math.exp(-cluster.energy/100.)
        
        
    def reconstruct_hcal(self, block, hcalid):
        '''
           block: element ids and edges 
           hcalid: id of the hcal being processed her
        
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
        #ask Colin - tracks and ecals group together so what does this mean for history, should we$
        #try and split it up better
        # hcal used to make ecal_in has a couple of possible issues
        particles = dict()
        tracks = []
        ecals = []
        hcal =block.pfevent.hcal_clusters[hcalid]
        
        assert(len(block.linked_ids(hcalid, "hcal_hcal"))==0  )
               
        for trackid in block.linked_ids(hcalid, "hcal_track"):
            tracks.append(block.pfevent.tracks[trackid])
            for ecalid in block.linked_ids(trackid, "ecal_track") :
                # the ecals get all grouped together for all tracks in the block
                # Maybe we want to link ecals to their closest track etc?
                # this might help with history work
                # ask colin.
                if not self.locked[ecalid] :
                    ecals.append(block.pfevent.ecal_clusters[ecalid])
                    self.locked[ecalid]  = True
                # hcal should be the only remaining linked hcal cluster (closest one)
                #thcals = [th for th in elem.linked if th.layer=='hcal_in']
                #assert(thcals[0]==hcal)
        print( 'Reconstruct Hcal {hcal}'.format(hcal=hcal) )
        print( '\tT {tracks}'.format(tracks=tracks) )
        print( '\tE {ecals}'.format(ecals=ecals) )
        hcal_energy = hcal.energy
        if len(tracks):
            ecal_energy = sum(ecal.energy for ecal in ecals)
            track_energy = sum(track.energy for track in tracks)
            for track in tracks:
                #make a charged hadron
                newparticle=self.reconstruct_track( track)
                particles[newparticle.uniqueid]=newparticle
                
            delta_e_rel = (hcal_energy + ecal_energy) / track_energy - 1.
            # WARNING
            # calo_eres = self.detector.elements['hcal'].energy_resolution(track_energy)
            calo_eres = self.neutral_hadron_energy_resolution(hcal)
            print( 'dE/p, res = {derel}, {res} '.format(
                derel = delta_e_rel,
                res = calo_eres ))
            if delta_e_rel > self.nsigma_hcal(hcal) * calo_eres: # approx means hcal energy + ecal energies > track energies
                
                excess = delta_e_rel * track_energy # energy in excess of track energies
                print( 'excess = {excess:5.2f}, ecal_E = {ecal_e:5.2f}, diff = {diff:5.2f}'.format(
                    excess=excess, ecal_e = ecal_energy, diff=excess-ecal_energy))
                if excess <= ecal_energy: # approx means hcal energy > track energies 
                    # Make a photon from the ecal energy
                    # We make only one photon using only the combined ecal energies
                    # ask Colin why we don't use individual ecals
                    # we construct using the hcal, it makes for a trickier time with setting up the history
                    # some ecals should be linked to the new particles.
                    newparticle = self.reconstruct_cluster(hcal, 'ecal_in',excess)
                    if newparticle:                                          
                        particles[newparticle.uniqueid]=newparticle
                else: # approx means that hcal energy>track energies so we must have a neutral hadron
                    #excess-ecal_energy is approximately hcal energy  - track energies
                    newparticle = self.reconstruct_cluster(hcal, 'hcal_in',
                                                        excess-ecal_energy)
                    if newparticle:
                        particles[newparticle.uniqueid]=newparticle
                    if ecal_energy:
                        #make a photon from the remaining ecal energies
                        #again history is confusingbecause hcal is used to provide direction
                        #be better to make several smaller photons one per ecal?
                        newparticle=self.reconstruct_cluster(hcal, 'ecal_in',
                                                                  ecal_energy)
                        if newparticle:
                            particles[newparticle.uniqueid]=newparticle

        else: # case whether there are no tracks make a neutral hadron for each hcal
              # note that hcal-ecal links have been removed so hcal should only be linked to 
              # other hcals
            
            for elem in hcal.linked:
                assert(elem.layer=='hcal_in')
                
            newparticle=self.reconstruct_cluster(hcal, 'hcal_in')
            if newparticle:
                particles[newparticle.uniqueid]=newparticle
            
        self.locked[hcalid] = True
        return particles 
                
    def reconstruct_cluster(self, cluster, layer, energy=None, vertex=None):
        '''construct a photon if it is an ecal
           construct a neutral hadron if it is an hcal
        '''        
        if vertex is None:
            vertex = TVector3()
        pdg_id = None
        if layer=='ecal_in':
            pdg_id = 22 #photon
        elif layer=='hcal_in':
            pdg_id = 130 #K0
        else:
            raise ValueError('layer must be equal to ecal_in or hcal_in')
        assert(pdg_id)
        mass, charge = particle_data[pdg_id]
        if energy is None:
            energy = cluster.energy
        if energy < mass: 
            return None 
        momentum = math.sqrt(energy**2 - mass**2)
        p3 = cluster.position.Unit() * momentum
        p4 = TLorentzVector(p3.Px(), p3.Py(), p3.Pz(), energy)
        particle = Reconstructed_Particle(p4, vertex, charge, pdg_id)
        if (pdg_id==22 and particle.p4().M()!=0):
            print cluster.uniqueid,cluster.energy
        
        path = StraightLine(p4, vertex)
        path.points[layer] = cluster.position #alice: this may be a bit strange because we can make a photon with a path where the point is actually that of the hcal?
                                            # nb this only is problem if the cluster and the assigned layer are different
        particle.set_path(path)
        particle.clusters[layer] = cluster  # not sure about this either when hcal is used to make an ecal cluster?
        self.locked[cluster.uniqueid] = True #just OK but not nice if hcal used to make ecal.
        return particle
        
    def reconstruct_track(self, track, clusters=None): # cluster argument does not ever seem to be used at present
        '''construct a charged hadron from the track
        '''
        vertex = track.path.points['vertex']
        pdg_id = 211 * track.charge
        mass, charge = particle_data[pdg_id]
        p4 = TLorentzVector()
        p4.SetVectM(track.p3, mass)
        particle = Reconstructed_Particle(p4, vertex, charge, pdg_id)
        
        particle.set_path(track.path)
        particle.clusters = clusters
        self.locked[track.uniqueid] = True
        return particle


    def __str__(self):
        
        #make this use the history information
        
        #if self.history_nodes!= None :
         #   for block in blocks:
                
        theStr = ['New Rec Particles:']
        theStr.extend( map(str, self.particles))
        theStr.append('Unused:')
        if len(self.unused)==0:
            theStr.append('None')
        else:
            theStr.extend( map(str, self.unused))
        return '\n'.join( theStr )
