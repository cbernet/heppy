from ROOT import TFile, TCanvas, TH1F, gPad
import time

holder = list()

class Plotter(object):
    
    def __init__(self, fname, opt=''):
        self.opt = opt
        self.root_file = TFile(fname)
        self.tree = self.root_file.Get('events')
        self.canvas = TCanvas("canvas", "canvas", 600,600)  
        
    def bfrac(self):    
        n_bfrac = self.tree.Draw('jet1_bfrac','jet1_bfrac>0.5', self.opt)
        n_tot = self.tree.GetEntries()
        return n_bfrac / float(n_tot)
    
    def beff(self):
        self.tree.Draw('jet1_b', 'jet1_bmatch==1')
        return self.tree.GetHistogram().GetMean()

if __name__ == '__main__':

    import sys
    
    if len(sys.argv)!=2:
        print 'usage <ZHTreeProducer root file>'
        sys.exit(1)
    
    plotter = Plotter(sys.argv[1])
    print plotter.bfrac()
    print plotter.beff()
