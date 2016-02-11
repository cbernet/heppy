import numpy as np
import sys

class Material(object):
    def __init__(self, name, x0, lambdaI):
        self.name = name
        self.x0 = x0
        self.lambdaI = lambdaI

    def path_length(self, ptc):
        '''path before decay within material'''
        freepath = self.x0 if ptc.is_em() else self.lambdaI
        if freepath == 0.0:
            return sys.float_info.max
        else: 
            return np.random.exponential(freepath)

void = Material('void', 0, 0)


if __name__ == '__main__':
    import matplotlib.pyplot as plt 
    a = np.random.exponential(25., 10000)
    n, bins, patches = plt.hist(a, 50, normed=1, facecolor='green', alpha=0.75)
    plt.show()
