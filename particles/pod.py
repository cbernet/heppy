import copy

class POD(object):
    '''Extends the cmg::PhysicsObject functionalities.'''

    def __init__(self, cpppod):
        self.cpppod = cpppod
        super(POD, self).__init__()

    def __copy__(self):
        '''Very dirty trick, the cpppod is deepcopied...'''
        cpppod = copy.deepcopy( self.cpppod )
        newone = type(self)(cpppod)
        newone.__dict__.update(self.__dict__)
        newone.cpppod = cpppod
        return newone        
        
    def __getattr__(self,name):
        '''all accessors  from cmg::DiTau are transferred to this class.'''
        return getattr(self.cpppod, name)

    def __eq__(self,other):
        if( hasattr(other, 'cpppod') ):
            # the two python PODs have the same C++ POD
            return self.cpppod == other.cpppod
        else:
            # can compare a python POD with a cpp POD directly
            return self.cpppod == other 

