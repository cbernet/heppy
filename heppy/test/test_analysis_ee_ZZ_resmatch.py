import unittest
import tempfile
import copy
import os
import shutil

from analysis_ee_ZZ_resmatch_cfg import config
from heppy.framework.looper import Looper
from ROOT import TFile

import logging
logging.getLogger().setLevel(logging.ERROR)

import heppy.statistics.rrandom as random

class TestAnalysis_ee_ZZ_resmatch(unittest.TestCase):

    def setUp(self):
        random.seed(0xdeadbeef)
        self.outdir = tempfile.mkdtemp()
        import logging
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        shutil.rmtree(self.outdir)
        logging.disable(logging.NOTSET)

    def test_1(self):
        '''
        '''
        fname = '/'.join([os.environ['HEPPY'],
                          'test/data/ee_ZZ_4mu.root'])
        config.components[0].files = [fname]
        looper = Looper( self.outdir, config,
                         nEvents=50,
                         nPrint=0 )
        looper.loop()
        looper.write()
    


if __name__ == '__main__':

    unittest.main()
