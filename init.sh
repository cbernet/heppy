

source /cvmfs/fcc.cern.ch/sw/views/releases/externals/94.2.0/x86_64-centos7-gcc62-opt/setup.sh


export HEPPY=$PWD/heppy
export PATH=$HEPPY/bin:$PATH
export PYTHONPATH=$PWD:$PYTHONPATH

# need this for heppy's context discovery. TODO: get rid of context discovery in heppy
export FCCEDM="unused"
export PODIO="unused"
export FCCPHYSICS="unused"

