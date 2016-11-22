class Weight(object):

    def __init__(self, weight):
        
        self.weight

    def weight(self):

        return self.weight()

    def __str__(self):
        tmp = '{className} : weight = {weight:5.1f}'
        return tmp.format(
            className = self.__class__.__name__,
            weight = self.weight()
            )
