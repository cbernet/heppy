class ParticlesComparer(object):

    def __init__(self,particlesA,particlesB):
        ''' Simple check that two sets of particles are the same
            will stop on an assert is things are different
            assumes particles are ordered in the same way
            is relatively naive but sufficient so far
        '''
        self.A = particlesA
        self.B = particlesB
        
        assert(len(self.A)==len(self.B))
        
        #sort A B
        for i in range(len(self.A)):
            assert(self.A[i].pdgid() == self.B[i].pdgid())
            assert(self.A[i].q() == self.B[i].q())
            assert(self.A[i].p4() == self.B[i].p4())
        
        