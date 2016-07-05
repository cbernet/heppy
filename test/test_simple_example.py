import unittest
import shutil
import os
import copy
from simple_example_cfg import config, stopper 
from heppy.utils.testtree import create_tree, remove_tree
from heppy.framework.looper import Looper
from heppy.framework.exceptions import UserStop
from ROOT import TFile

import logging
logging.getLogger().setLevel(logging.ERROR)

class TestSimpleExample(unittest.TestCase):

    def setUp(self):
        self.fname = create_tree()
        rootfile = TFile(self.fname)
        self.nevents = rootfile.Get('test_tree').GetEntries()
        self.outdir = 'Out_test'

    def test_all_events_processed(self):
        loop = Looper( self.outdir, config,
                       nEvents=None,
                       nPrint=0,
                       timeReport=True)
        loop.loop()
        loop.write()
        logfile = open('/'.join([self.outdir, 'log.txt']))
        nev_processed = None
        for line in logfile:
            if line.startswith('number of events processed:'):
                nev_processed = int(line.split(':')[1])
        logfile.close()
        self.assertEqual(nev_processed, self.nevents)
        # checking the looper itself.
        self.assertEqual(loop.nEvProcessed, self.nevents)

    def test_skip(self):
        first = 10 
        loop = Looper( self.outdir, config,
                       nEvents=None,
                       firstEvent=first,
                       nPrint=0,
                       timeReport=True)
        loop.loop()
        loop.write()
        # input file has 200 entries
        # we skip 10 entries, so we process 190.
        self.assertEqual(loop.nEvProcessed, self.nevents-first)

    def test_process_event(self):
        loop = Looper( self.outdir, config,
                       nEvents=None,
                       nPrint=0,
                       timeReport=True)
        loop.process(10)
        self.assertEqual(loop.event.input.var1, 10)
        loop.process(10)
        
    def test_userstop(self):
        config_with_stopper = copy.copy(config)
        config_with_stopper.sequence.insert(1, stopper)
        loop = Looper( self.outdir, config_with_stopper,
                       nEvents=None,
                       nPrint=0,
                       timeReport=True)
        self.assertRaises(UserStop, loop.process, 10)
  


if __name__ == '__main__':

    unittest.main()
