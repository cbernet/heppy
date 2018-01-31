import unittest
import tempfile
import copy
import os
import shutil
import heppy.framework.context as context

#Runs a Clic Z analysis and checks the pdebug output against a master document

if context.name == 'fcc':

    from analysis_ee_Z_cfg import config
    from heppy.framework.looper import Looper
    from ROOT import TFile

    import logging
    logging.getLogger().setLevel(logging.ERROR)
    
    import heppy.statistics.rrandom as random

    class TestAnalysis_ee_Z(unittest.TestCase):

        def setUp(self):
            random.seed(0xdeadbeef)
            self.outdir = tempfile.mkdtemp()
            import logging
            #Alice: I turned this off otherwise no pdebug output. Ask Colin why it is on and if this is OK
            #logging.disable(logging.CRITICAL)

        def tearDown(self):
            shutil.rmtree(self.outdir)
            logging.disable(logging.NOTSET)

        
        # NB If this test fails and If you expected the physics results to change 
        # then it means that the cpp version of papas will need to be updated.
        # Please
        # (1) take the physics_clic.txt file that is produced by this test and rename it to update
        # the required_clic_physics_dd.txt file in heppy/test/data
        # (2) notify alice to change papas cpp
        def test_z_clic(self):
            '''Check Z mass in ee->Z->ddbar (CLIC).
            Will fail if physics algorithms are modified,
            so should probably be removed from test suite,
            or better: be made optional. 
            '''
            random.seed(0xdeadbeef)
            from heppy.papas.detectors.CLIC import clic
            fname = '/'.join([os.environ['HEPPY'],
                                      'test/data/ee_Z_ddbar.root'])
            config.components[0].files = [fname]
            for s in config.sequence:
                if hasattr( s,'detector'):
                    s.detector = clic
                if hasattr(s, 'debug_filename'):
                    s.debug_filename = 'physics_clic.txt'
            self.looper = Looper( self.outdir, config,
                                  nEvents=10,
                                  nPrint=0 )            
            self.looper.loop()
            self.looper.write()
            self.assertEqual(0,os.system("source $HEPPY/test/data/pdebug_python_check.sh  physics_clic.txt $HEPPY/test/data/required_clic_physics_dd.txt"))

if __name__ == '__main__':

    unittest.main()
