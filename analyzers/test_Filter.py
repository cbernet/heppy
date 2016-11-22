import unittest
import os
import shutil
import tempfile
from Selector import Selector 
from heppy.framework.event import Event
import heppy.framework.config as cfg

class SelectorTestCase(unittest.TestCase):

    def setUp(self):
        self.outdir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.outdir)
    
    def test_list(self):
        event = Event(0)
        event.the_list = range(10)
        cfg_ana = cfg.Analyzer(
            Selector,
            output = 'filtered',
            input_objects = 'the_list',
            filter_func = lambda x : x%2 == 0
            )
        cfg_comp = cfg.Component(
            'test',
            files = []
            )
        filter = Selector(cfg_ana, cfg_comp, self.outdir)
        filter.process(event)
        self.assertItemsEqual(event.filtered, [0,2,4,6,8])
    
    def test_dict(self):
        event = Event(0)
        event.the_dict = dict( [ (x, x**2) for x in range(10) ] )
        cfg_ana = cfg.Analyzer(
            Selector,
            output = 'filtered',
            input_objects = 'the_dict',
            filter_func = lambda x : x == 9
            )
        cfg_comp = cfg.Component(
            'test',
            files = []
            )
        filter = Selector(cfg_ana, cfg_comp, self.outdir)
        filter.process(event)
        self.assertDictEqual(event.filtered, {3:9})
        
if __name__ == '__main__':
    unittest.main()
