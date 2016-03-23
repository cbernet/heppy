from numpy.testing.utils import assert_allclose

class ParticlesComparer(object):

    def __init__(self,particlesA,particlesB):
        ''' Simple check that two sets of sorted particles are the same
            will stop on an assert is things are different
            assumes particles are ordered in the same way
            is relatively naive but sufficient so far
        '''
        self.A = particlesA
        self.B = particlesB
        
        assert(len(self.A)==len(self.B))
        
        for i in range(len(self.A)):
            assert_allclose(self.A[i].pdgid() , self.B[i].pdgid(),rtol=1e-8, atol=0.0000001 )
            assert_allclose(self.A[i].q() , self.B[i].q(),rtol=1e-8, atol=0.0000001 )
            assert_allclose(self.A[i].p4().M() , self.B[i].p4().M(),rtol=1e-8, atol=0.0000001 )
            assert_allclose(self.A[i].p4().X() , self.B[i].p4().X(),rtol=1e-8, atol=0.0000001 )
            assert_allclose(self.A[i].p4().Y() , self.B[i].p4().Y(),rtol=1e-8, atol=0.0000001 )
            assert_allclose(self.A[i].p4().Z() , self.B[i].p4().Z(),rtol=1e-8, atol=0.0000001 )
            
        #print "compared: ", len(self.A)
        
        