import unittest
import shutil
from simple_example_cfg import *
from heppy.utils.testtree import create_tree, remove_tree
from heppy.framework.looper import Looper
from ROOT import TFile

import logging
logging.getLogger().setLevel(logging.ERROR)

class TestSimpleExample(unittest.TestCase):

    def setUp(self):
        self.fname = create_tree()
        rootfile = TFile(self.fname)
        self.nevents = rootfile.Get('test_tree').GetEntries()

    def test_all_events_processed(self):
        outdir = 'Out_TestSimpleExample'
        if os.path.isdir(outdir):
            shutil.rmtree(outdir)
        loop = Looper( outdir, config,
                       nEvents=None,
                       nPrint=0,
                       timeReport=True)
        loop.loop()
        loop.write()
        logfile = open('/'.join([outdir, 'log.txt']))
        nev_processed = None
        for line in logfile:
            if line.startswith('number of events processed:'):
                nev_processed = int(line.split(':')[1])
        self.assertEqual(nev_processed, self.nevents)
                
if __name__ == '__main__':

    unittest.main()
