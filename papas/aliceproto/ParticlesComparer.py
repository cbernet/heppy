class ParticlesComparer(object):

    def __init__(self,particlesA,particlesB):
        self.A = particlesA
        self.B = particlesB
        
        assert(len(self.A)==len(self.B))
        
        #sort A B
        for i in range(len(self.A)):
            print i
            assert(self.A[i].pdgid()==self.B[i].pdgid())
            assert(self.A[i].pt()==self.B[i].pt())
            assert(self.A[i].eta()==self.B[i].eta())
            assert(self.A[i].q()==self.B[i].q())
            assert(self.A[i].e()==self.B[i].e())
            assert(self.A[i].phi()==self.B[i].phi())
            assert(self.A[i].m()==self.B[i].m())
            assert(self.A[i].p4()==self.B[i].p4())
        
        