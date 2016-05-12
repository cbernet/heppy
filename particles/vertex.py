
class Vertex(object):
    '''Interface for vertices. 
    Make sure your code satisfies this interface.
    Specializations in cms, fcc, and tlv packages
    '''
    def __init__(self, *args, **kwargs):
        super(Vertex, self).__init__(*args, **kwargs)
    
    def x(self):
        return self._point.X()

    def y(self):
        return self._point.Y()

    def z(self):
        return self._point.Z()

    def position(self):
        return self._point

    def ctau(self):
        return self._ctau
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        tmp = '{className} : x = {x:5.2f}, y = {y:5.2f}, z = {z:5.2f}, ctau = {ctau:5.2f}'
        return tmp.format(
            className = self.__class__.__name__,
            x = self.x(),
            y = self.y(),
            z = self.z(),
            ctau = self.ctau(),
            )

    def __repr__(self):
        return str(self)
    
