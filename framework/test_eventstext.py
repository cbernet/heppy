import unittest
import os 
import pickle
import tempfile
from eventstext import Events

def create_data():
    data = []
    for i in range(100):
        event = dict(x1=i, x2=i**2)
        data.append(event)
    test_file = tempfile.NamedTemporaryFile(delete=False)
    pickle.dump(data, test_file)
    return test_file.name 

class EventsTextTestCase(unittest.TestCase):

    def setUp(self):
        fname = create_data()
        self.events = Events(fname)
        
    def test_iterate(self):
        '''Test iteration'''
        for ev in self.events:
            pass
        self.assertTrue(True)

    def test_get(self):
        '''Test direct event access'''
        event = self.events[2]
        self.assertEqual(event.x1, 2.)
        self.assertEqual(event.x2, 4.)


if __name__ == '__main__':
    unittest.main()
