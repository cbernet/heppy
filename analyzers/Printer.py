from framework.analyzer import Analyzer

class Printer(Analyzer):

    def process(self, event):
        print "printing event", event.iEv
        store = event.input
        jets = store.get("GenJet")
        for jet in jets:
            print 'jet', jet.P4().Pt
