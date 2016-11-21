'''background rate vs signal efficiency'''

import numpy as np
import scipy as sp
import scipy.interpolate
import heppy.statistics.rrandom as random


class ROC(object):
    '''background rate vs signal efficiency'''
    
    def __init__(self, sig_bgd_points):
        '''
        
        @param sig_bgd_points: list of a few points on the curve::

          [ [eff1, bgnd_eff_1],
            [eff2, bgnd_eff_2] ... ]
            
        A linear interpolation is performed in lin-log space when using
        the roc curve.
        '''
        self.sig_bgd_points = sig_bgd_points
        lin_interp = scipy.interpolate.interp1d(sig_bgd_points[:, 0],
                                                np.log10(sig_bgd_points[:, 1]), 
                                                'linear')
        self.roc = lambda zz: np.power(10.0, lin_interp(zz))
        
    def plot(self):
        '''Plot the curve.'''
        xx = np.linspace(min(self.sig_bgd_points[:, 0]),
                         max(self.sig_bgd_points[:, 0]))
        plt.plot(xx, self.roc(xx))
        plt.show()
        
    def set_working_point(self, eff):
        '''Set working point.
        
        The efficiency and background rate can then be accessed as
         - self.eff
         - self.fake_rate
         
        @param b_eff: desired efficiency
        '''
        self.eff = eff
        self.fake_rate = self.roc(eff)
        
    def is_tagged(self, is_signal):
        '''Return tagging value.
        
        @return: result of the tagging (boolean)
        @param is_b: specifies whether the object of interest is signal
          or background
        '''
        eff = self.eff if is_signal else self.fake_rate
        return random.uniform(0, 1) < eff
        


cms_roc = ROC(
    np.array(
    [ 
     [0.4, 2.e-4],
     [0.5, 7.e-4],
     [0.6, 3.e-3],
     [0.7, 1.5e-2], 
     [0.8, 7.e-2],
     [0.9, 3.e-1], 
     [1., 1.]]
    )
)  
       

