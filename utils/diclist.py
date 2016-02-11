# Copyright (C) 2014 Colin Bernet
# https://github.com/cbernet/heppy/blob/master/LICENSE

class diclist( list ):

    def __init__(self):
        super( diclist, self).__init__()
        self.dico = {}

    def add( self, key, value ):
        if key in self.dico:
            raise ValueError("key '{key}' already exists".format(key=key) )
        self.dico[key] = len(self)
        self.append(value)

    def __getitem__(self, index):
        '''These functions are quite risky...cannot use an integer as key...'''
        try:
            # index = int( index )
            return super(diclist, self).__getitem__(index)
        except TypeError, ValueError:
            return super(diclist, self).__getitem__( self.dico[index] )
            
    def __setitem__(self, index, value):
        '''These functions are quite risky...'''
        try:
            # why did I add this cast? it's casting string to int...
            # index = int( index )
            return super(diclist, self).__setitem__(index, value)
        except TypeError,ValueError:
            return super(diclist, self).__setitem__( self.dico[index], value )
            

    
