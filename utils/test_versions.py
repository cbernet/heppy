import unittest
import heppy

scriptfname = '/'.join([
    heppy.__path__[0], 
    'test/simple_example_cfg.py'
    ])
from versions import Versions

########################################################################
class TestVersion(unittest.TestCase):
    """"""

    #----------------------------------------------------------------------
    def setUp(self):
        """"""
        self.versions = Versions(scriptfname)
        print self.versions

    #----------------------------------------------------------------------
    def test_1_yaml(self):
        """"""
        fname = 'software.yaml'
        self.versions.write_yaml(fname)
        import yaml
        with open(fname) as infile:
            data = yaml.load(infile)
            self.assertEqual(data['software']['heppy'],
                             self.versions.tracked['heppy']['commitid'])
        
if __name__ == '__main__':
    unittest.main()
