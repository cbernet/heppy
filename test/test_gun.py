import unittest
import tempfile
import copy
import os
import shutil
import logging
logging.getLogger().setLevel(logging.ERROR)

import heppy.statistics.rrandom as random

import heppy.framework.context as context
if context.name == 'fcc':

    from gun_papas_cfg import config
    from heppy.framework.looper import Looper

@unittest.skipIf(context.name=='bare', 'ROOT not available')
class TestAnalysis_gun(unittest.TestCase):

    def setUp(self):
        random.seed(0xdeadbeef)
        self.outdir = tempfile.mkdtemp()
        import logging
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        shutil.rmtree(self.outdir)
        logging.disable(logging.NOTSET)

    def test_gun(self):
        '''test that the particle gun runs
        '''
        self.looper = Looper( self.outdir, config,
                              nEvents=100,
                              nPrint=0 )
        self.looper.loop()
        self.looper.write()
        

if __name__ == '__main__':

    unittest.main()
