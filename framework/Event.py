import collections

class Event(object):
    '''Event class.

    The Looper passes the Event object to each of its Analyzers,
    which in turn can:
    - read some information
    - add more information
    - modify existing information.
    '''

    def __init__(self, iEv):
        self.iEv = iEv
        self.eventWeight = 1

    def __str__(self):
        header = '{type}: {iEv}'.format( type=self.__class__.__name__,
                                         iEv = self.iEv)
        varlines = []
        for var,value in sorted(vars(self).iteritems()):
            tmp = value
            if isinstance( value, collections.Iterable ) and \
                   not isinstance( value, (str,unicode)) and \
                   not str(iter( value )).startswith('<ROOT.reco::candidate'):
                tmp = map(str, value)

            varlines.append( '\t{var:<15}:   {value}'.format(var=var, value=tmp) )
        all = [ header ]
        all.extend(varlines)
        return '\n'.join( all )
