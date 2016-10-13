import unittest
import shutil
import tempfile
import os
import copy
import glob
from simple_example_cfg import config, stopper 
from heppy.utils.testtree import create_tree, remove_tree
from heppy.scripts.heppy_loop import create_parser, main
from heppy.framework.looper import Looper
from heppy.framework.exceptions import UserStop
from ROOT import TFile

import logging
logging.getLogger().setLevel(logging.ERROR)

class TestSimpleExample(unittest.TestCase):

    def setUp(self):
        self.fname = create_tree()
        self.fname2 = self.fname.replace('.root','_2.root')
        shutil.copy(self.fname, self.fname2)
        rootfile = TFile(self.fname)
        self.nevents = rootfile.Get('test_tree').GetEntries()
        self.outdir = tempfile.mkdtemp()
        logging.disable(logging.CRITICAL)
        
    def tearDown(self):
        shutil.rmtree(self.outdir)
        logging.disable(logging.NOTSET)
        os.remove(self.fname2)

    def test_multiprocessing(self): 
        parser = create_parser()
        options, args = parser.parse_args()
        options.iEvent = None
        options.nprint = 0
        main(options, [self.outdir, 'simple_multi_example_cfg.py'])
        wcard = '/'.join([self.outdir, 
                          'test_component_Chunk*',
                          'heppy.analyzers.examples.simple.SimpleTreeProducer.SimpleTreeProducer_tree/simple_tree.root'
                          ])
        output_root_files = glob.glob(wcard)
        self.assertEqual(len(output_root_files),2)
        

if __name__ == '__main__':

    unittest.main()
