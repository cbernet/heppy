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
    
    from heppy.test.plot_ee_b import Plotter
    from heppy.framework.looper import Looper
    from heppy.configuration import from_fccsw
    from ROOT import TFile
    from analysis_ee_Z_bb_cfg import config
    

@unittest.skipIf(context.name=='bare', 'ROOT not available')
class TestAnalysis_ee_Z_bb(unittest.TestCase):

    def setUp(self):
        random.seed(0xdeadbeef)
        self.outdir = tempfile.mkdtemp()
        import logging
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        shutil.rmtree(self.outdir)
        logging.disable(logging.NOTSET)

    def test_beff_cms(self):
        '''Check b matching probability and b tag efficiency in CMS 
        '''
        from heppy.papas.detectors.CMS import cms
        fname = '/'.join([os.environ['HEPPY'],
                          'test/data/ee_Z_bbbar.root'])
        config.components[0].files = [fname]
        for s in config.sequence:
            if hasattr( s,'detector'):
                s.detector = cms
        self.looper = Looper( self.outdir, config,
                              nEvents=500,
                              nPrint=0 )
        self.looper.loop()
        self.looper.write()
        rootfile = '/'.join([self.outdir,
                            'heppy.analyzers.JetTreeProducer.JetTreeProducer_1/jet_tree.root '])
        plotter = Plotter(rootfile)
        self.assertAlmostEqual(plotter.bfrac(), 0.867, places=2)
        self.assertAlmostEqual(plotter.beff(), 0.71, places=2)

    def test_fake_cms(self):
        '''Check fake rate in CMS
        '''
        from heppy.papas.detectors.CMS import cms
        fname = '/'.join([os.environ['HEPPY'],
                          'test/data/ee_Z_ddbar.root'])
        config.components[0].files = [fname]
        for s in config.sequence:
            if hasattr( s,'detector'):
                s.detector = cms
        self.looper = Looper( self.outdir, config,
                              nEvents=100,
                              nPrint=0 )
        self.looper.loop()
        self.looper.write()
        rootfile = '/'.join([self.outdir,
                             'heppy.analyzers.JetTreeProducer.JetTreeProducer_1/jet_tree.root '])



        

if __name__ == '__main__':

    unittest.main()
