
from ROOT import gSystem
gSystem.Load("libpapascpp") #check with Colin if this is OK or if should be made to execute just once
from ROOT import  randomgen

class RRandom(object):
    
    @staticmethod
    def expovariate (a):
        thing = u = randomgen.RandExponential(a)
        u = thing.next()
        #print u
        return u
    
    @staticmethod
    def uniform (a, b):
        thing = randomgen.RandUniform(a, b)
        u = thing.next()
        #print u
        return u
    
    @staticmethod
    def gauss (a, b):
        thing = randomgen.RandNormal(a, b)
        u = thing.next()
        #print u
        return u    
    
    @staticmethod
    def seed (s):
        thing = randomgen.RandUniform(0, 1)
        thing.setSeed(s)
    