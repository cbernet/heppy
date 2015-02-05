
export HEPPY=$PWD
export PATH=$HEPPY/bin:$PATH
export PYTHONPATH=$PWD/..:$PYTHONPATH

# set up executable directory
cd $HEPPY/bin
ln -sf ../scripts/*.py .
ln -sf ../scripts/heppy .
chmod +x * 
cd .. > /dev/null

