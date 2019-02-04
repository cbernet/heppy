
from ROOT import TRandom

rootrandom = TRandom()

def expovariate (a):
    x=rootrandom.Exp(1./a)
    return x

def uniform (a, b):
    x=rootrandom.Uniform(a, b)
    return x

def gauss (a, b):
    x= rootrandom.Gaus(a,b)
    return x

def seed (s):
    global rootrandom
    rootrandom = TRandom(s)
