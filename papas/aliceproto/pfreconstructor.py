from heppy.papas.aliceproto.identifier import Identifier
from heppy.papas.aliceproto.blocksplitter import BlockSplitter
from heppy.papas.pdt import particle_data
from heppy.papas.path import StraightLine, Helix
from heppy.papas.pfobjects import Particle

from ROOT import TVector3, TLorentzVector
import math
import pprint

class PFReconstructor(object):

    def __init__(self,event):
        self.blocks=event.blocks
        
        for block in self.blocks.itervalues():
            splitblocks = self.simplifiedblocks(block,event.history_nodes)
            #del self.blocks[block.uniqueid]
            self.blocks.update(splitblocks)
            
        for block in self.blocks.itervalues():    
            self.reconstruct_block(block)
        
    def reconstruct(self, block):
        particles = []
        all_subgroups = dict()
        # pprint.pprint( links.groups )
        # import pdb; pdb.set_trace()
        for groupid, group in links.groups.iteritems():
            if self.simplify_group(group):
                all_subgroups[groupid] = links.subgroups(groupid)
        for group_id, subgroups in all_subgroups.iteritems():
            del links.groups[group_id]
            links.groups.update(subgroups)
        for group_id, group in links.groups.iteritems():
            self.log.info( "group {group_id} {group}".format(
                group_id = group_id,
                group = group) ) 
            self.particles.extend( self.reconstruct_group(group) )
        self.unused = [elem for elem in links.elements if not elem.locked]
        self.log.info("Particles:")
        self.log.info(str(self))
            
    def simplifiedblocks(self, block,history_nodes=None):
        # for each track, keeping only the closest hcal link
        splitblocks=dict()
        ids=block.element_uniqueids
        assert(len(ids)!=0)
        if len(ids)==1:
            return block
        
        #sort ids by type
        #sort edges by distance
        to_unlink = []        
        for id in ids :
            if Identifier.is_track(id) :
                linked = block.linked_edges(id,"hcal_track") #sorted from small to large distance
                if linked!=None :
                    first_hcal = True
                    for elem in linked:
                        if first_hcal:
                            first_hcal = False
                        else:
                            to_unlink.append(elem)
            elif Identifier.is_ecal(id) :
                # remove all ecal-hcal links. ecal linked to hcal give rise to a photon anyway.
                linked = block.linked_edges(id,"ecal_hcal")
                to_unlink.append(linked)
        if (linked != None) :
            return BlockSplitter(block,to_unlink,history_nodes).blocks
        splitblocks[block.uniqueid]=block
        return splitblocks
            
    def reconstruct_block(self, block):
        particles = []
        ids=block.element_uniqueids
        self.locked=dict()
        for id in ids:
            self.locked[id] = False
        
       
        if len(ids)==1: #TODO WARNING!!! LOTS OF MISSING CASES
            id = ids[0]
            elem=block.pfevent.getobject(id)
            if Identifier.is_ecal(id) :
                particles.append(self.reconstruct_cluster(block.pfevent.ecal_clusters[id],"ecal_in"))
            elif Identifier.is_hcal(id) :
                particles.append(self.reconstruct_cluster(block.pfevent.hcal_clusters[id],"hcal_in"))
            elif Identifier.is_track(id) :
                particles.append(self.reconstruct_track(block.pfevent.tracks[id]))
            #TODO elem.locked = True
        else: #TODO
            for id in ids :
                if Identifier.is_hcal(id) :
                    particles.extend(self.reconstruct_hcal(block,id))
            for id in ids :
                if Identifier.is_track(id) and not self.locked[id] :
                # unused tracks, so not linked to HCAL
                # reconstructing charged hadrons.
                # ELECTRONS TO BE DEALT WITH.
                    particles.append(self.reconstruct_track(block.pfevent.tracks[id]))
                    # tracks possibly linked to ecal->locking cluster
                    for idlink in block.linked_ids(id,"ecal_track") :
                        locked[idlink] = True
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
        
        
    def reconstruct_hcal(self, block,hcalid):
        particles = []
        tracks = []
        ecals = []
        hcal =block.pfevent.hcal_clusters[hcalid]
        
        assert(len(block.linked_ids(hcalid, "hcal_hcal"))==0  )
               
        for trackid in block.linked_ids(hcalid, "hcal_track"):
            tracks.append(block.pfevent.tracks[trackid])
            for ecalid in block.linked_ids(trackid, "ecal_track") :
                if not locked[ecalid] :
                    ecals.append(block.pfevent.ecal_clusters[ecalid])
                    self.locked[ecalid]  = True
                # hcal should be the only remaining linked hcal cluster (closest one)
                #thcals = [th for th in elem.linked if th.layer=='hcal_in']
                #assert(thcals[0]==hcal)
        print( hcalid )
        print( '\tT {tracks}'.format(tracks=tracks) )
        print( '\tE {ecals}'.format(ecals=ecals) )
        hcal_energy = hcal.energy
        if len(tracks):
            ecal_energy = sum(ecal.energy for ecal in ecals)
            track_energy = sum(track.energy for track in tracks)
            for track in tracks:
                particles.append(self.reconstruct_track( track))
            delta_e_rel = (hcal_energy + ecal_energy) / track_energy - 1.
            # WARNING
            # calo_eres = self.detector.elements['hcal'].energy_resolution(track_energy)
            calo_eres = self.neutral_hadron_energy_resolution(hcal)
            print( 'dE/p, res = {derel}, {res} '.format(
                derel = delta_e_rel,
                res = calo_eres ))
            if delta_e_rel > self.nsigma_hcal(hcal) * calo_eres:
                excess = delta_e_rel * track_energy
                self.log.info( 'excess = {excess:5.2f}, ecal_E = {ecal_e:5.2f}, diff = {diff:5.2f}'.format(
                    excess=excess, ecal_e = ecal_energy, diff=excess-ecal_energy))
                if excess <= ecal_energy:
                    particles.append(self.reconstruct_cluster(hcal, 'ecal_in',
                                                              excess))
                else:
                    particle = self.reconstruct_cluster(hcal, 'hcal_in',
                                                        excess-ecal_energy)
                    if particle:
                        particles.append(particle)
                    if ecal_energy:
                        particles.append(self.reconstruct_cluster(hcal, 'ecal_in',
                                                                  ecal_energy))

        else:
            # hcal cluster linked to other hcal clusters 
            for elem in hcal.linked:
                assert(elem.layer=='hcal_in')
                # ecal hcal links have been cut
            particles.append(self.reconstruct_cluster(hcal, 'hcal_in'))
        hcal.locked = True
        return particles 
                
    def reconstruct_cluster(self, cluster, layer, energy=None, vertex=None):
        if vertex is None:
            vertex = TVector3()
        pdg_id = None
        if layer=='ecal_in':
            pdg_id = 22
        elif layer=='hcal_in':
            pdg_id = 130
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
        particle = Particle(p4, vertex, charge, pdg_id)
        path = StraightLine(p4, vertex)
        path.points[layer] = cluster.position
        particle.set_path(path)
        particle.clusters[layer] = cluster
        cluster.locked = True
        return particle
        
    def reconstruct_track(self, track, clusters=None):
        vertex = track.path.points['vertex']
        pdg_id = 211 * track.charge
        mass, charge = particle_data[pdg_id]
        p4 = TLorentzVector()
        p4.SetVectM(track.p3, mass)
        particle = Particle(p4, vertex, charge, pdg_id)
        particle.set_path(track.path)
        particle.clusters = clusters
        track.locked = True
        return particle


    def __str__(self):
        theStr = ['Particles:']
        theStr.extend( map(str, self.particles))
        theStr.append('Unused:')
        if len(self.unused)==0:
            theStr.append('None')
        else:
            theStr.extend( map(str, self.unused))
        return '\n'.join( theStr )
