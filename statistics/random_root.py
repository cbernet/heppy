
from ROOT import TRandom

rootrandom = TRandom()

def expovariate (a):
    return rootrandom.Exp(1./a)

def uniform (a, b):
    return rootrandom.Uniform(a, b)


def gauss (a, b):
    return rootrandom.Gaus(a,b)


def seed (s):
    global rootrandom
    rootrandom = TRandom(0xdeadbeef)
