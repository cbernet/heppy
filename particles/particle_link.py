
class Particle_Link(object):
    '''Interface for link between two particles, contains the ids of each particle
    Make sure your code satisfies this interface.
    Specializations in cms, fcc, and tlv packages
    '''
    def __init__(self, *args, **kwargs):
        super(Particle_Link, self).__init__(*args, **kwargs)

    def parentid(self):
        return self._parentid

    def childid(self):
        return self._childid

    def __str__(self):
        tmp = '{className} : parent = {s}, child = {s}'
        return tmp.format(
            className = self.__class__.__name__,
            parentid =_parentid,
            childid = _childid,
            )

    def __repr__(self):
        return str(self)

