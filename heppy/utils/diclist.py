# Copyright (C) 2014 Colin Bernet
# https://github.com/cbernet/heppy/blob/master/LICENSE

class diclist( list ):
    '''list with an internal dictionary for indexing, 
    allowing to keep dictionary elements ordered. 
    keys can be everything except an integer.
    '''

    def __init__(self):
        super( diclist, self).__init__()
        # internal dictionary, will contain key -> index in list
        self.dico = {}
        self.__indexed__keys = {}

    def add( self, key, value ):
        if isinstance(key, (int, long)):
            raise ValueError("key cannot be an integer")
        if key in self.dico:
            raise ValueError("key '{key}' already exists".format(key=key) )
        index = len(self)
        self.dico[key] = index
        self.__indexed__keys[index] = key
        self.append(value)

##  This is complicated, need to re-index the two dictionaries...       
##    def rm(self, key):
##        if isinstance(key, (int, long)):
##            raise ValueError("key cannot be an integer")
##        if not key in self.dico:
##            raise ValueError("key '{key}' does not exist".format(key=key) )
##        index = self.dico[key]
##        self.pop(index)
##        del self.dico[key]
##        self.__indexed__keys = dict()
##        for key

    def values(self):
        '''dictionary signature. preserves ordering'''
        return self
    
    def iteritems(self):
        '''dictionary signature. preserves ordering'''
        for index, value in enumerate(self):
            yield self.__indexed__keys[index], value
            
    def keys(self):
        '''dictionary signature. preserves ordering'''
        keys = []
        for index, value in enumerate(self):
            keys.append(self.__indexed__keys[index])
        return keys

    def __setitem__(self, index, value):
        self.add(index, value)

    def __getitem__(self, index):
        '''index can be a dictionary key, or an integer specifying 
        the rank of the value to be accessed
        '''
        try:
            # if index is an integer (the rank), use the list. 
            return super(diclist, self).__getitem__(index)
        except TypeError, ValueError:
            # else it's the dictionary key.
            # use the internal dictionary to get the index, 
            # and return the corresponding value from the list
            return super(diclist, self).__getitem__( self.dico[index] )
            
            

    
