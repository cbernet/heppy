export HEPPY=$PWD
echo prepending $HEPPY/bin to PATH
export PATH=$HEPPY/bin:$PATH

# set up executable directory
cd $HEPPY/bin
ln -sf ../scripts/*.py .
chmod +x * 
cd ..
