import unittest
import tempfile
import copy
import os
import shutil


from analysis_ee_ZH_cfg import config
from heppy.test.plot_ee_ZH import plot
from heppy.framework.looper import Looper
from heppy.framework.exceptions import UserStop
from ROOT import TFile

import logging
logging.getLogger().setLevel(logging.ERROR)

class TestAnalysis_ee_ZH(unittest.TestCase):

    def setUp(self):
        self.outdir = tempfile.mkdtemp()
        fname = '/'.join([os.environ['HEPPY'],
                          'test/data/ee_ZH_Zmumu_Hbb.root'])
        config.components[0].files = [fname]
        self.looper = Looper( self.outdir, config,
                              nEvents=100,
                              nPrint=0,
                              timeReport=True)
        import logging
        logging.disable(logging.CRITICAL)
        
    def tearDown(self):
        shutil.rmtree(self.outdir)
        logging.disable(logging.NOTSET)

    def test_analysis(self):
        self.looper.loop()
        self.looper.write()
        rootfile = '/'.join([self.outdir,
                            'heppy.analyzers.examples.zh.ZHTreeProducer.ZHTreeProducer_1/tree.root'])
        mean, sigma = plot(rootfile)
        self.assertTrue(abs(mean-125.) < 5)
        self.assertTrue(abs(sigma-20.) < 5)
        


if __name__ == '__main__':

    unittest.main()
