if [ -n "$CMSSW_BASE" ] 
then
	echo $CMSSW_BASE
	mkdir python 
	cd python 
	ln -sf .. heppy
	echo installing heppy in $PWD
	cd - > /dev/null
else
	export HEPPY=$PWD
	echo prepending $HEPPY/bin to PATH
	export PATH=$HEPPY/bin:$PATH

	# set up executable directory
	cd $HEPPY/bin
	ln -sf ../scripts/*.py .
	chmod +x * 
	cd .. > /dev/null
fi
