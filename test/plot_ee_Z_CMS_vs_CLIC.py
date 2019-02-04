from ROOT import TFile, TCanvas, TH1F, gPad
from tdrstyle import tdrstyle
from cpyroot import sBlack, sBlue
import sys



class MassPlot(object):
    def __init__(self, fname, style, canvas=None):
        self.file = TFile(fname)
        self.tree = self.file.Get('events')
        opt = ''
        if not canvas: 
            self.canvas = TCanvas("canvas", "canvas", 600,600)
        else:
            canvas.cd()
            opt = 'same'
        self.hist = TH1F("hist", ";mass of all particles (GeV)", 120, 0, 120)
        style.formatHisto(self.hist)
        self.hist.SetFillStyle(0)
        self.hist.SetStats(0)
        self.tree.Draw('sum_all_m>>hist', '', opt)
        xmin = self.hist.GetMean() - self.hist.GetRMS() * 2.
        xmax = self.hist.GetMean() + self.hist.GetRMS() * 2.
        self.hist.Fit("gaus", "LM", "", xmin, xmax)
        gPad.Update()
        func = self.hist.GetFunction("gaus")
        print func.GetParameter(1), func.GetParameter(2)


        
if __name__ == '__main__':

    import sys
    
    if len(sys.argv)!=3:
        print 'usage plot <CMS fname> <CLIC fname>'
        sys.exit(1)

    cmsfname, clicfname = sys.argv[1:]
    clic = MassPlot(clicfname, sBlack)
    cms = MassPlot(cmsfname, sBlue, clic.canvas)
