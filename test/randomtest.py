
# setting the random seed for reproducible results
import sys
from heppy.framework.looper import Looper

#import random
from heppy.statistics.rrandom import RRandom as random

if __name__ == '__main__':

    random.seed(0xdeadbeef)

    print random.uniform(0, 1)
    print random.uniform(0, 1)
    print random.expovariate(3)
    print random.expovariate(4)
    random.seed(0xdeadbeef)

    print random.uniform(0, 1)
    print random.uniform(0, 1)
    print random.expovariate(3)
    print random.expovariate(4)
    
    
    pass