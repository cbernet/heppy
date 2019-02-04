import pickle   
        
class Events(object):
    
    def __init__(self, filenames, dummy=None):
        # for now only one file supported
        filename = filenames[0]
        with open(filename) as the_file:
            self.data = pickle.load(the_file)
        
    def __getattr__(self, attr):
        return self._curevent[attr]
 
    def __iter__(self):
        return iter(self.data)
    
    def __getitem__(self, index):
        self._curevent = self.data[index]
        return self  
    
    def __len__(self):
        return len(self.data)