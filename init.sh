export HEPPY=$PWD

echo prepending $HEPPY to PYTHONPATH
export PYTHONPATH=$HEPPY:$PYTHONPATH

echo prepending $HEPPY/bin to PATH
export PATH=$HEPPY/bin:$PATH

# set up executable directory
cd $HEPPY/bin
ln -sf ../framework/multiloop.py 
chmod +x * 
cd ..
