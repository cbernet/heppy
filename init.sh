export HEPPY=$PWD

echo prepending $ALBERS/examples/python to PYTHONPATH
export PYTHONPATH=$ALBERS/examples/python:$PYTHONPATH

echo prepending $HEPPY to PYTHONPATH
export PYTHONPATH=$HEPPY:$PYTHONPATH

echo prepending $HEPPY/bin to PATH
export PATH=$HEPPY/bin:$PATH

# set up executable directory
cd $HEPPY/bin
ln -sf ../framework/multiloop.py 
chmod +x * 
cd ..
