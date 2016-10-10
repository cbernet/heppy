import pprint
import copy
import collections
import fnmatch

from ROOT import TChain

class Event(object):
    '''Event class.

    The Looper passes an Event object to each of its Analyzers,
    which in turn can:
    - read some information
    - add more information
    - modify existing information.

    A printout can be obtained by doing e.g.:
    
      event = Event() 
      print event 

    The printout can be controlled by the following class attributes:
      print_nstrip : number of items in sequence to be printed before stripping the following items
      print_patterns : list of patterns. By default, this list is set to ['*'] so that all attributes are
                    printed

    Example:
      event = Event()
      Event.print_nstrip = 5  # print only the 5 first items of sequences
      Event.print_patterns = ['*particles*', 'jet*'] # only print the attributes that 
                                                     # contain "particles" in their name or
                                                     # have a name starting by "jet" 
       
    Object attributes:
      iEv = event processing index, starting at 0
      eventWeight = a weight, set to 1 at the beginning of the processing
      input = input, as determined by the looper
    #TODO: provide a clear interface for access control (put, get, del products) - we should keep track of the name and id of the analyzer.
    '''

    print_nstrip = 10
    print_patterns = ['*']

    def __init__(self, iEv, input_data=None, setup=None, eventWeight=1):
        self.iEv = iEv
        self.input = input_data
        self.setup = setup
        self.eventWeight = eventWeight

    def _get_stripped_attrs(self, subname=""):
        selected_attrs = copy.copy(self.__dict__)
        selected_attrs.pop('setup')
        selected_attrs.pop('input')
        stripped_attrs = dict()
        new_attrs = dict()
        for name, value in selected_attrs.iteritems():
            if any([fnmatch.fnmatch(name, pattern) for pattern in self.__class__.print_patterns]):
                stripped_attrs[subname + name] = value
        for name, value in stripped_attrs.iteritems():
            if isinstance(value, Event): # deal with an Event within the Event
                new_attrs.update(value._get_stripped_attrs(value.__class__.__name__ + ": "))
            else: #add in elements of the event but stop after n elements
                new_attrs.update(self._first_n_elements(name, value))

        stripped_attrs.update(new_attrs) 
        return stripped_attrs

    def _first_n_elements(self,name,value):
        #recursive, will return a dict (limited to print_nstrip elements)
        #Note this function allows for dicts of dicts or lists
        #contents of lists are not handled recursively
        newdata=dict()
        if hasattr(value, '__len__') and isinstance(value, collections.Mapping): #dict:      
            subdict = dict()
            for newname, entry in value.iteritems(): #allow recursion in case this dict contains a dict
                subdict.update(self._first_n_elements(newname, entry)) 
            if len(value) > self.__class__.print_nstrip+1: #use only part of the dict
                entries = [entry for  entry in subdict.iteritems()]
                entries = entries[:self.__class__.print_nstrip]
                entries.append(("...", "...")) # no guarantees where abouts this is printed
                newdata[name] = dict(entries) 
            else: #not too big so using whole dict is OK
                newdata[name] = subdict 
        elif hasattr(value, '__len__') and len(value)>self.__class__.print_nstrip+1: #list 
            newdata[name] = [val for val in value[:self.__class__.print_nstrip]]
            newdata[name].append('...')
            newdata[name].append(value[-1])   
        else:
            newdata[name] = value
        return newdata    

    def __str__(self):
        header = '{type}: {iEv}'.format(type=self.__class__.__name__, iEv=self.iEv)
        stripped_attrs = self._get_stripped_attrs() #allows other events such as papasevent to also be printed like an Event
        contents = pprint.pformat(stripped_attrs, indent=4)
        return '\n'.join([header, contents])
