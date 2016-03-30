from pyLCIO import IOIMPL

class Events(object):
    
    def __init__(self, filename):
        self.reader = IOIMPL.LCFactory.getInstance().createLCReader() 
        self.reader.open(filename)
        
    def __len__(self):
        return self.reader.getNumberOfEvent()

    def __getattr__(self, key):
        return getattr(self.events, key)

    def __getitem__(self, iEv):
        pass 
