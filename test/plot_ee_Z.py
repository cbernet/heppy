from ROOT import TFile, TCanvas, TH1F, gPad
import time

holder = list()
tree = None

def plot_ee_mass(fname, nbins=100, xmin=70, xmax=100):
    global tree
    root_file = TFile(fname)
    tree = root_file.Get('events')
    canvas = TCanvas("canvas", "canvas", 600,600)  
    hist = TH1F("hist", ";mass of all particles (GeV)", nbins, 0, 200)
    tree.Draw('sum_all_m>>hist', '', '')
    xmin = hist.GetMean() - hist.GetRMS() * 2.
    xmax = hist.GetMean() + hist.GetRMS() * 2.
    hist.Fit("gaus", "LM", "", xmin, xmax)
    gPad.Update()
    gPad.SaveAs('sum_all_m.png')
    time.sleep(1)
    func = hist.GetFunction("gaus")
    holder.extend([root_file, tree, canvas, hist, func])
    return func.GetParameter(1), func.GetParameter(2)

if __name__ == '__main__':

    import sys
    
    if len(sys.argv)!=2:
        print 'usage <ZHTreeProducer root file>'
        sys.exit(1)

    mean, sigma = plot_ee_mass(sys.argv[1])
    print 'fit: mean = {mean:5.2f} sigma = {sigma:5.2f} resolution = {res:5.2f}'.format(
        mean=mean, sigma=sigma, res=sigma/mean*100)
    
    
