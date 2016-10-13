import unittest
import shutil
import tempfile
import os
import copy
import glob
from simple_example_cfg import config, stopper 
from heppy.utils.testtree import create_tree, remove_tree
from heppy.framework.looper import Looper
from heppy.framework.exceptions import UserStop
from ROOT import TFile

import logging
logging.getLogger().setLevel(logging.ERROR)

class TestMultiProcessing(unittest.TestCase):

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
        from heppy.scripts.heppy_loop import create_parser, main
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
        
    def test_heppy_batch(self):
        from heppy.scripts.heppy_batch import create_batch_manager, main
        batchManager = create_batch_manager() 
        options, args = batchManager.ParseOptions()
        options.iEvent = None
        options.nprint = 0     
        options.outputDir = self.outdir
        options.batch = 'nohup ./batchScript.sh &'
        main(options, ['simple_multi_example_cfg.py'], batchManager)
        wcard = '/'.join([self.outdir, 
                          'test_component_Chunk*',
                          'heppy.analyzers.examples.simple.SimpleTreeProducer.SimpleTreeProducer_tree/simple_tree.root'
                          ])
        import time 
        time.sleep(5)
        output_root_files = glob.glob(wcard)
        self.assertEqual(len(output_root_files),2)
        

if __name__ == '__main__':

    unittest.main()
