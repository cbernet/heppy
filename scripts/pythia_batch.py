import os
import shutil
import re
from heppy.utils.batchmanager import BatchManager


def batchScriptLocal(index, cardfname):
    '''prepare a local version of the batch script, to run using nohup'''

    script = """#!/bin/bash
echo 'running job' {index}
echo
fcc-pythia8-generate {cardfname}
""".format(index=index, cardfname=cardfname) 
    return script


def batchScriptCERN_FCC(index, cardfname):
   '''prepare the LSF version of the batch script, to run on LSF'''

   dirCopy = """echo 'sending the logs back'  # will send also root files if copy failed
cp *.root $LS_SUBCWD
if [ $? -ne 0 ]; then
   echo 'ERROR: problem copying job directory back'
else
   echo 'job directory copy succeeded'
fi"""
   cpCmd=dirCopy

   script = """#!/bin/bash
#BSUB -q 8nm
# ulimit -v 3000000 # NO
unset LD_LIBRARY_PATH
echo 'copying job dir to worker'
source /afs/cern.ch/exp/fcc/sw/0.8pre/setup.sh
cd $HEPPY
source ./init.sh
echo 'environment:'
echo
env | sort
echo
which python
cd -
cp -rf $LS_SUBCWD .
ls
cd `find . -type d | grep /`
echo 'running'
fcc-pythia8-generate {cardfname}   
echo
{copy}
""".format(cardfname=cardfname, copy=cpCmd)

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
            scriptFile.write( batchScriptCERN_FCC(jobDir,
                                                  self.cardfname) )
        elif mode == 'LOCAL':
            scriptFile.write( batchScriptLocal(value,
                                               self.cardfname) )
        scriptFile.close()
        os.system('chmod +x %s' % scriptFileName)
        configfile = open('/'.join([jobDir, self.cardfname]), 'w')
        configfile.writelines(self.config)
        configfile.close()
        
def build_config(fname, nevents):
    '''make sure that pythia config file has the correct seeding
    parameters, and set the number of events.
    '''
    nevents_pattern = re.compile('\s*Main:numberOfEvents\s*=\s*\d+.*')
    ifile = open(fname)
    config = ifile.readlines()
    newconfig = []
    for line in config:
        if nevents_pattern.match(line):
            line = 'Main:numberOfEvents = {}\n'.format(nevents) 
        newconfig.append(line)
    newconfig.extend([  
        'Random:setSeed = on\n',
        'Random:seed = 0\n'
    ])   
    ifile.close()
    return newconfig

def main(options, args, batchManager):
    if len(args) != 3:
        batchManager.Parser().error('incorrect number of arguments')
    cardfname, njobs, nevents = args
    njobs = int(njobs)
    nevents = int(nevents)
    print cardfname, njobs, nevents
    
    batchManager.config = build_config(cardfname, nevents)
    batchManager.cardfname = cardfname
    
    listOfValues = range(njobs)
    batchManager.PrepareJobs( listOfValues )
    waitingTime = 0.1
    batchManager.SubmitJobs( waitingTime )


if __name__ == '__main__':
    batchManager = MyBatchManager()
    batchManager.parser_.usage="""
    %prog [options] <pythia_card_file> <njobs> <nevents>

    Run fcc-pythia8-generate on the batch. 
    """
    options, args = batchManager.ParseOptions()
    main(options, args, batchManager)
