import os
import shutil
from heppy.utils.batchmanager import BatchManager


def batchScriptLocal(index, cardfname):
    '''prepare a local version of the batch script, to run using nohup'''

    script = """#!/bin/bash
echo 'running job' {index}
echo
fcc-pythia8-generate {cardfname}
""".format(index=index, cardfname=cardfname) 
    return script


class MyBatchManager( BatchManager ):
    '''Batch manager for fcc-pythia8-generate''' 

    def PrepareJobUser(self, jobDir, value ):
        '''Prepare one job. This function is called by the base class.'''
        print jobDir, value
        #prepare the batch script
        scriptFileName = jobDir+'/batchScript.sh'
        scriptFile = open(scriptFileName,'w')
        mode = self.RunningMode(self.options_.batch)
        if mode == 'LXPLUS':
            scriptFile.write( batchScriptLXPLUS(jobDir,
                                                self.cardfname) )
        elif mode == 'LOCAL':
            scriptFile.write( batchScriptLocal(value,
                                               self.cardfname) )
        scriptFile.close()
        os.system('chmod +x %s' % scriptFileName)
        shutil.copy(self.cardfname, jobDir)


def main(options, args, batchManager):
    if len(args) != 2:
        batchManager.Parser().error('incorrect number of arguments')
    cardfname, njobs = args
    njobs = int(njobs)
    batchManager.cardfname = cardfname
    print cardfname, njobs
    
    listOfValues = range(njobs)
    batchManager.PrepareJobs( listOfValues )
    waitingTime = 0.1
    batchManager.SubmitJobs( waitingTime )


if __name__ == '__main__':
    batchManager = MyBatchManager()
    batchManager.parser_.usage="""
    %prog [options] <pythia_card_file> <njobs>

    Run fcc-pythia8-generate on the batch. 
    """
    options, args = batchManager.ParseOptions()
    main(options, args, batchManager)
