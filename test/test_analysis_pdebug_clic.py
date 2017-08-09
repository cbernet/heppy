import unittest
import tempfile
import copy
import os
import shutil
import heppy.framework.context as context

#Runs a Clic Z analysis and checks the pdebug output against a master document

if context.name == 'fcc':

    from analysis_ee_Z_cfg import config
    from heppy.test.plot_ee_Z import plot_ee_mass
    from heppy.framework.looper import Looper
    from ROOT import TFile

    import logging
    #todo check with Colin regarding the logging level which turns off pdebug also
    #logging.getLogger().setLevel(logging.ERROR)
    logging.getLogger().setLevel(logging.INFO)
    
    import heppy.statistics.rrandom as random

    class TestAnalysis_ee_Z(unittest.TestCase):

        def setUp(self):
            random.seed(0xdeadbeef)
            self.outdir = tempfile.mkdtemp()
            import logging
            #logging.disable(logging.CRITICAL)

        def tearDown(self):
            shutil.rmtree(self.outdir)
            logging.disable(logging.NOTSET)

        

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
