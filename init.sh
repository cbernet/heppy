
export HEPPY=$PWD
export PATH=$HEPPY/bin:$PATH
export PYTHONPATH=$PWD/..:$PYTHONPATH

# set up executable directory
cp scripts/*.py bin/
cp scripts/heppy bin/
chmod +x bin/*.py 
chmod +x bin/heppy


