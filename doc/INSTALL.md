#Heppy : Installation Instructions 


## Prerequisites

Heppy only depends on python and ROOT (if you intend to read events from a ROOT file), making the installation fairly simple. If you're using heppy in the context of the CMS or FCC software on SLC6, you're all set and you can proceed to the [next section](#environment)

**python 2.x, x>5**

On top of python, you need the following python packages: 

     numpy
     ipython  (not strictly needed, but really useful)

To get them, install pip and use it to install these packages.

**ROOT 5, with pyroot support (optional)**

Note that you need to ensure that ROOT was compiled with the same
version of python as the one in your PATH.

To check that, do the following:

	python
	import ROOT

Any error message needs to be taken care of before going further. 


## Environment 

From this directory, run the initialization script, which makes a few
executable scripts available to you:

    source ./init.sh
    
Check that you can now import heppy:

    python
    import heppy 

