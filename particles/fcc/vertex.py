
class Vertex(object):

    def __init__(self, fccvertex):
        self.fccvertex = fccvertex
        self.incoming = []
        self.outgoing = []

    def __hash__(self):
        return hash( (self.fccvertex.containerID(), self.fccvertex.index()) )

    def __eq__(self, other):
        return self.fccvertex ==other.fccvertex
