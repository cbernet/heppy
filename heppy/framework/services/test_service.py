import unittest
import os 
import shutil
import heppy.framework.config as cfg
import heppy.framework.context as context
if context.name != 'bare':
    from tfile import TFileService

@unittest.skipIf(context.name=='bare', 'ROOT not available')
class ServiceTestCase(unittest.TestCase):

    def test_tfile(self):
        config = cfg.Service(TFileService, 
                             'myhists', 
                             fname = 'histos.root', 
                             option = 'recreate')
        dummy = None
        dirname = 'test_dir'
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        os.mkdir(dirname)
        fileservice = TFileService(config, dummy, dirname)
        fileservice.start()
        fileservice.stop()
        shutil.rmtree(dirname)

if __name__ == '__main__':
    unittest.main()
