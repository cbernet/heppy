import sys
from ROOT import TFile, TCanvas, TH1F, gPad

if len(sys.argv)!=2:
    print 'usage <ZHTreeProducer root file>'
    sys.exit(1)

root_file = TFile(sys.argv[1])
tree = root_file.Get('events')
tree.Print()

canvas = TCanvas("canvas", "canvas", 600,600)

h = TH1F("h", "higgs di-jet mass;m_{jj} (GeV)", 50, 0, 200)
tree.Draw('higgs_m>>h', 'zed_m>50') 
h.GetYaxis().SetRangeUser(0, 120)
gPad.Update()
gPad.SaveAs('ee_ZH_mjj.png')
