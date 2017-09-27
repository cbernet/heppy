import copy

from p4 import P4
from heppy.papas.data.identifier import Identifier

class Particle(P4):
    '''Interface for particles. 
    Make sure your code satisfies this interface.
    Specializations in cms, fcc, and tlv packages
    '''
    def __init__(self, *args, **kwargs):
        super(Particle, self).__init__(*args, **kwargs)
    
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

    def uniqueid(self):
        '''unique Identifier'''
        return self._uid

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        tmp = '{className} : {idstr} : pdgid = {pdgid:5}, status = {status:3}, q = {q:2}, {p4}'
        idstr = "none"
        if self.uniqueid()!=0 :
            idstr = '{pretty:6}:{uid}'.format(
                pretty=Identifier.pretty(self.uniqueid()),
                uid=self.uniqueid())
        return tmp.format(
            className = self.__class__.__name__,
            idstr = idstr,
            pdgid = self.pdgid(),
            status = self.status(),
            q = self.q(),
            p4 = super(Particle, self).__str__()
            )
