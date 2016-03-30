import unittest
from simple_example_cfg import *
from heppy.utils.testtree import create_tree, remove_tree
from heppy.framework.looper import Looper

import logging
logging.getLogger().setLevel(logging.ERROR)

class TestSimpleExample(unittest.TestCase):

    def setUp(self):
        create_tree()

    def test_1(self):
        loop = Looper( 'looper', config,
                       nEvents=None,
                       nPrint=0,
                       timeReport=True)
        loop.loop()
        loop.write()
        
if __name__ == '__main__':

    unittest.main()
