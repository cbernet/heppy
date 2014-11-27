from heppy.framework.services.service import Service
from ROOT import TFile

class TFileService(Service):

    def __init__(self, cfg, comp, outdir):
        fname = '/'.join([outdir, cfg.fname])
        self.file = TFile(fname, cfg.option)
        
    def stop(self):
        self.file.Write() 
        self.file.Close()

if __name__ == '__main__':
    fileservice = TFileService('test.root', 'recreate')
    fileservice.start()
    fileservice.stop()
