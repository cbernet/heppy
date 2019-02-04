import pickle

class Event(object):
    
    def __init__(self, the_dict):
        self._dict = the_dict
        
    def __getattr__(self, attr):
        return self._dict[attr]
    
    def __setattr__(self, attr, value):
        setattr(self._dict, attr, value)
        
        
class Events(object):
    
    def __init__(self, filename, dummy=None):
        with open(filename) as the_file:
            self.data = pickle.load(the_file)
            # self.data = [Event(evdata) for evdata in tmp]
        
    def __getattr__(self, attr):
        return self._curevent[attr]
 
    def __iter__(self):
        return iter(self.data)
    
    def __getitem__(self, index):
        self._curevent = self.data[index]
        return self  