from framework.Analyzer import Analyzer

class Printer(Analyzer):

    def process(self, event):
        print "printing event", event.iEv
        print event
