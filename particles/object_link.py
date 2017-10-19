
class ObjectLink(object):
    '''Interface for link between two objects, contains the ids of each object
    Make sure your code satisfies this interface.
    Specializations in cms, fcc, and tlv packages
    '''
    def __init__(self, *args, **kwargs):
        super(ObjectLink, self).__init__(*args, **kwargs)

    def id1(self):
        return self._id1

    def id2(self):
        return self._id2

    def __str__(self):
        tmp = '{className} : id1 = {id1}, id2 = {id2}'
        return tmp.format(
            className = self.__class__.__name__,
            id1 =self._id1,
            id2 =self._id2
            )

    def __repr__(self):
        return str(self)


