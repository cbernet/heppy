import unittest
import shutil
import tempfile
import os
import copy
from heppy.framework.looper import Looper
from text_example_cfg import config

import logging
logging.getLogger().setLevel(logging.ERROR)

class TestSimpleExample(unittest.TestCase):

    def setUp(self):
        self.outdir = tempfile.mkdtemp()
        logging.disable(logging.CRITICAL)
        
    def tearDown(self):
        shutil.rmtree(self.outdir)
        logging.disable(logging.NOTSET)
    

    def test_all_events_processed(self):
        loop = Looper( self.outdir, config,
                       nEvents=None,
                       nPrint=0 )
        loop.loop()
        
    def test_skip(self):
        first = 10 
        loop = Looper( self.outdir, config,
                       nEvents=None,
                       firstEvent=first,
                       nPrint=0 )
        loop.loop()    

    def test_process_event(self):
        loop = Looper( self.outdir, config,
                       nEvents=None,
                       nPrint=0 )
        loop.process(10)
        self.assertEqual(loop.event.input.x1, 10)
        self.assertEqual(loop.event.input.x2, 100)
        
if __name__ == '__main__':

    unittest.main()
