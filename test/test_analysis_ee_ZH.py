import unittest
import tempfile
import copy
import os
import shutil

import heppy.utils.pdebug
from analysis_ee_ZH_cfg import config
from heppy.test.plot_ee_ZH import plot
from heppy.framework.looper import Looper
from heppy.framework.exceptions import UserStop
from ROOT import TFile


import logging
logging.getLogger().setLevel(logging.ERROR)


def test_sorted(ptcs):
    from heppy.configuration import Collider
    keyname = 'pt'
    if Collider.BEAMS == 'ee':
        keyname = 'e'
    pt_or_e = getattr(ptcs[0].__class__, keyname)
    values = [pt_or_e(ptc) for ptc in ptcs]
    return values == sorted(values, reverse=True)


class TestAnalysis_ee_ZH(unittest.TestCase):

    def setUp(self):
        self.outdir = tempfile.mkdtemp()
        fname = '/'.join([os.environ['HEPPY'],
                          'test/data/ee_ZH_Zmumu_Hbb.root'])
        config.components[0].files = [fname]
        self.looper = Looper( self.outdir, config,
                              nEvents=10,
                              nPrint=0,
                              timeReport=True)
        import logging
        logging.disable(logging.CRITICAL)
        
    def tearDown(self):
        shutil.rmtree(self.outdir)
        logging.disable(logging.NOTSET)

    def test_analysis(self):
        '''Check for an almost perfect match with reference.
        Will fail if physics algorithms are modified,
        so should probably be removed from test suite,
        or better: be made optional. 
        '''
        self.looper.loop()
        self.looper.write()
        rootfile = '/'.join([self.outdir,
                            'heppy.analyzers.examples.zh.ZHTreeProducer.ZHTreeProducer_1/tree.root'])
        mean, sigma = plot(rootfile)
        import random
        print random.getstate()
        print mean, sigma
        self.assertAlmostEqual(mean, 118.3, 1)
        self.assertAlmostEqual(sigma, 31.0, 1)
        
    def test_analysis_sorting(self):
        self.looper.process(0)
        self.assertTrue(test_sorted(self.looper.event.rec_particles))
    
        


if __name__ == '__main__':

    unittest.main()
