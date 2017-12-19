import unittest
import tempfile
import copy
import os
import shutil

#Runs a CMS ZZ mumu bbar analysis and checks the pdebug output against a master document

import heppy.framework.context as context

if context.name == 'fcc':

    from analysis_ee_ZH_cfg import config
    from heppy.framework.looper import Looper
    from ROOT import TFile

    import logging
    logging.getLogger().setLevel(logging.ERROR)

    import heppy.statistics.rrandom as random



    class TestAnalysis_ee_ZH_debug(unittest.TestCase):

        def setUp(self):
            random.seed(0xdeadbeef)
            self.outdir = tempfile.mkdtemp()
            import logging
            #logging.disable(logging.CRITICAL)

        def tearDown(self):
            shutil.rmtree(self.outdir)
            logging.disable(logging.NOTSET)

        # NB If this test fails and If you expected the physics results to change 
        # then it means that the cpp version of papas will need to be updated.
        # Please
        # (1) take the physics_cms.txt that is produced by this test and rename it to update
        # the required_cms_physics.txt file in heppy/test/data
        # (2) notify alice to change papas cpp
        def test_analysis_ee_ZH_mumubb(self):
            '''Check for an almost perfect match with reference.
            Will fail if physics algorithms are modified,
            so should probably be removed from test suite,
            or better: be made optional. 
            '''
            from heppy.papas.detectors.CMS import cms
            for s in config.sequence:
                if hasattr( s,'detector'):
                    s.detector = cms
                if hasattr(s, 'debug_filename'):
                    s.debug_filename = 'physics_cms.txt'
            # import pdb; pdb.set_trace()
            fname = '/'.join([os.environ['HEPPY'],
                                      'test/data/ee_ZH_Zmumu_Hbb.root'])
            config.components[0].files = [fname]
            looper = Looper( self.outdir, config,
                                          nEvents=10,
                                          nPrint=0 )
            looper.loop()
            looper.write()
            self.assertEqual(0,os.system("source $HEPPY/test/data/pdebug_python_check.sh  physics_cms.txt $HEPPY/test/data/required_cms_physics.txt"))
            


if __name__ == '__main__':

    unittest.main()
