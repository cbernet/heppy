class Events(list):
    '''A dummy event list class providing empty input Event.
    temporarily replaces the fwlite event list class.
    need to replace by a generator, or a source file.
    '''
    def __init__(self, nevents=10):
        super(Events, self).__init__(range(0,nevents))

    def size(self):
        return len(self)

    def to(self, iEv):
        '''navigate to event iEv.'''
        return self[iEv]

if __name__ == '__main__':
    events = Events()
    for ev in events:
        print ev
