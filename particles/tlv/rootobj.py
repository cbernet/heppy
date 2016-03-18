from itertools import count
import copy

class RootObj(object):

    _ids = count(0)
    
    def __init__(self, *args, **kwargs):
        super(RootObj, self).__init__(*args, **kwargs)
        self.objid = self._ids.next()

    def __eq__(self, other):
        try:
            return self.objid == other.objid
        except AttributeError:
            import pdb; pdb.set_trace()
    
