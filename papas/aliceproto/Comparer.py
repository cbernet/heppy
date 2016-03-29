from numpy.testing.utils import assert_allclose

class ParticlesComparer(object):

    def __init__(self,particlesA,particlesB):
        ''' Simple check that two sets of sensible sorted particles are the same
            will stop on an assert if things are different
            assumes particles are ordered in the same way
            is relatively naive but sufficient so far
        '''
        self.A = particlesA
        self.B = particlesB
        
        assert(len(self.A)==len(self.B))
        
        for i in range(len(self.A)):
            #print self.A[i]
            #print self.B[i]
            assert_allclose(self.A[i].pdgid(),  self.B[i].pdgid(),  rtol=1e-8, atol=0.0000001 )
            assert_allclose(self.A[i].q(),      self.B[i].q(),      rtol=1e-8, atol=0.0000001 )
            assert_allclose(self.A[i].p4().M(), self.B[i].p4().M(), rtol=1e-8, atol=0.0000001 )
            assert_allclose(self.A[i].p4().X(), self.B[i].p4().X(), rtol=1e-8, atol=0.0000001 )
            assert_allclose(self.A[i].p4().Y(), self.B[i].p4().Y(), rtol=1e-8, atol=0.0000001 )
            assert_allclose(self.A[i].p4().Z(), self.B[i].p4().Z(), rtol=1e-8, atol=0.0000001 )
            
        #print "compared: ", len(self.A)
class ClusterComparer(object):

    def __init__(self,clustersA,clustersB):
        ''' Simple check that two sets of sensible sorted particles are the same
            will stop on an assert if things are different
            assumes particles are ordered in the same way
            is relatively naive but sufficient so far
        '''
        self.A = clustersA
        self.B = clustersB
        self.A = sorted( self.A.values(),
                            key = lambda ptc: ptc.energy, reverse=True)        
        self.B = sorted( self.B.values(),
                            key = lambda ptc: ptc.energy, reverse=True)         
        assert(len(self.A)==len(self.B))
        
        for i in range(len(self.A)):
            print self.A[i]
            print self.B[i]
            AS = sorted( self.A[i].subclusters, key = lambda x: x.uniqueid)
            BS = sorted( self.B[i].subclusters, key = lambda x: x.uniqueid)            
            for j in range(len(self.A[i].subclusters)):
                print AS[j].uniqueid, BS[j].uniqueid   
                assert (AS[j].uniqueid== BS[j].uniqueid)
            assert_allclose(self.A[i].energy,  self.B[i].energy,  rtol=1e-12, atol=0.00000000001 )
            assert_allclose(self.A[i].position.Theta(),      self.B[i].position.Theta(),      rtol=1e-12, atol=0.00000000001 )
            assert_allclose(self.A[i].position.Phi() , self.B[i].position.Phi(), rtol=1e-12, atol=0.00000000001 )
            assert_allclose(self.A[i]._size, self.B[i]._size, rtol=1e-12, atol=0.00000000001 )
            
            assert_allclose(self.A[i].position.Mag(), self.B[i].position.Mag(), rtol=1e-12, atol=0.00000000001 )
            assert_allclose(self.A[i].position.X(), self.B[i].position.X(), rtol=1e-12, atol=0.00000000001 )
            assert_allclose(self.A[i].position.Y(), self.B[i].position.Y(), rtol=1e-12, atol=0.00000000001 )
            assert_allclose(self.A[i].position.Z(), self.B[i].position.Z(), rtol=1e-12, atol=0.00000000001 ) 
            assert_allclose(self.A[i]._angularsize, self.B[i]._angularsize, rtol=1e-12, atol=0.00000000001 )
            assert(len(self.A[i].subclusters)== len(self.B[i].subclusters) )
           
           
                #assert(AS[j].uniqueid==BS[j].uniqueid)
            
class TrackComparer(object):

    def __init__(self,tracksA,tracksB):
        ''' Simple check that two sets of sensible sorted particles are the same
            will stop on an assert if things are different
            assumes particles are ordered in the same way
            is relatively naive but sufficient so far
        '''
        self.A = tracksA
        self.B = tracksB
        self.A = sorted( self.A.values(),
                            key = lambda ptc: ptc.energy, reverse=True)        
        self.B = sorted( self.B.values(),
                            key = lambda ptc: ptc.energy, reverse=True)         
        assert(len(self.A)==len(self.B))
        
        for i in range(len(self.A)):
            print self.A[i]
            print self.B[i]
            assert_allclose(self.A[i].energy,  self.B[i].energy,  rtol=1e-8, atol=0.0000001 )
            assert_allclose(self.A[i].pt,      self.B[i].pt,      rtol=1e-8, atol=0.0000001 )
            assert_allclose(self.A[i].charge , self.B[i].charge , rtol=1e-8, atol=0.0000001 )
            
            
                    
            
                    
            