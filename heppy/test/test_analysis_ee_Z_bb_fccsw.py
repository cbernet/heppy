import unittest
import tempfile
import copy
import os
import shutil

import heppy.framework.context as context

if context.name == 'fcc':

    from heppy.test.plot_ee_b import Plotter
    from heppy.framework.looper import Looper
    from heppy.configuration import from_fccsw
    from_fccsw = True
    from analysis_ee_Z_bb_cfg import config    
    from ROOT import TFile

    import logging
    logging.getLogger().setLevel(logging.ERROR)

    import heppy.statistics.rrandom as random
    

    class TestAnalysis_ee_Z_bb_fccsw(unittest.TestCase):

        def setUp(self):
            random.seed(0xdeadbeef)
            self.outdir = tempfile.mkdtemp()
            import logging
            logging.disable(logging.CRITICAL)

        def tearDown(self):
            shutil.rmtree(self.outdir)
            logging.disable(logging.NOTSET)

        def test_beff_cms_fccsw(self):
            '''check that the analysis runs with papas inputs from cmssw
            '''
            from heppy.papas.detectors.CMS import cms
            fname = '/'.join([os.environ['HEPPY'],
                              'test/data/ee_Z_bbbar_with_papas_rec.root'])
            config.components[0].files = [fname]
            for s in config.sequence:
                if hasattr( s,'detector'):
                    s.detector = cms
            self.looper = Looper( self.outdir, config,
                                  nEvents=100,
                                  nPrint=0 )
            self.looper.loop()


if __name__ == '__main__':

    unittest.main()
