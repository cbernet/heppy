import copy

from p4 import P4
from heppy.papas.data.idcoder import IdCoder

class Particle(P4):
    '''Interface for particles. 
    Make sure your code satisfies this interface.
    Specializations in cms, fcc, and tlv packages
    '''
    def __init__(self, *args, **kwargs):
        super(Particle, self).__init__(*args, **kwargs)
        self._dagid = None
    
    def pdgid(self):
        '''particle type'''
        return self._pid

    def q(self):
        '''particle charge'''
        return self._charge

    def status(self):
        '''status code, e.g. from generator. 1:stable.'''
        return self._status

    def start_vertex(self):
        '''start vertex (3d point)'''
        return self._start_vertex 

    def end_vertex(self):
        '''end vertex (3d point)'''
        return self._end_vertex

    def set_dagid(self, dagid):
        '''unique DAG Identifier'''
        self._dagid = dagid
    
    def dagid(self):
        '''unique DAG Identifier'''
        return self._dagid  
    
    def dagid_str(self):
        return ""
    
    def objid(self):
        '''unique Identifier'''
        return self._objid        

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        tmp = '{className} :{idstr} pdgid = {pdgid:5}, status = {status:3}, q = {q:2}, {p4}'
        idstr = self.dagid_str()
        return tmp.format(
            className = self.__class__.__name__,
            idstr = idstr,
            pdgid = self.pdgid(),
            status = self.status(),
            q = self.q(),
            p4 = super(Particle, self).__str__()
            )
