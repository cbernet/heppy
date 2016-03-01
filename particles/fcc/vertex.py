from pod import POD

class Vertex(POD):

    def __init__(self, fccobj):
        self.fccobj = fccobj
        self.incoming = []
        self.outgoing = []

    # def __eq__(self, other):
    #     return self.fccvertex ==other.fccvertex
