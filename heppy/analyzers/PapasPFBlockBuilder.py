from heppy.framework.analyzer import Analyzer
from heppy.papas.pfalgo.pfblockbuilder import PFBlockBuilder
from heppy.papas.data.papasevent import PapasEvent
from heppy.papas.pfalgo.distance  import Distance


class PapasPFBlockBuilder(Analyzer):
    ''' Module to construct blocks of connected clusters and tracks 
        particles will eventually be reconstructed from elements of a block
        
        Usage:
        from heppy.analyzers.PapasPFBlockBuilder import PapasPFBlockBuilder
        pfblocks = cfg.Analyzer(
            PapasPFBlockBuilder,
            track_type_and_subtype = 'ts', 
            ecal_type_and_subtype = 'em', 
            hcal_type_and_subtype = 'hm'
        )
        
        track_type_and_subtype:  key for tracks collection in papasevent
        ecal_type_and_subtype: key for ecals collection in papasevent
        hcal_type_and_subtype: key for hcals collection in papasevent
        
    '''
    def __init__(self, *args, **kwargs):
        super(PapasPFBlockBuilder, self).__init__(*args, **kwargs)
        
                
    def process(self, event):
        papasevent = event.papasevent
        distance = Distance()
        uniqueids= []
        if self.cfg_ana.track_type_and_subtype:
            collection = papasevent.get_collection(self.cfg_ana.track_type_and_subtype)
            if collection:
                uniqueids += collection.keys()
        if self.cfg_ana.ecal_type_and_subtype:
            collection = papasevent.get_collection(self.cfg_ana.ecal_type_and_subtype) 
            if collection:
                uniqueids += collection.keys()            
        if self.cfg_ana.hcal_type_and_subtype:
            collection = papasevent.get_collection(self.cfg_ana.hcal_type_and_subtype)
            if collection:
                uniqueids += collection.keys()            
        blockbuilder = PFBlockBuilder(papasevent, uniqueids, distance, startindex=0)  
        papasevent.add_collection(blockbuilder.blocks)

        
