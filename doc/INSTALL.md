Heppy : Installation Instructions 
=================================

Prerequisites
-------------

Heppy only depends on python and ROOT, making the installation fairly simple.

**python 2.x, x>5**

On top of python, you need the following python packages: 

     numpy
     ipython  (not strictly needed, but really useful)

To get them, install pip and use it to install these packages.


**ROOT 5, with pyroot support**

Note that you need to ensure that ROOT was compiled with the same
version of python as the one in your PATH.

To check that, do the following:

    python
    import ROOT

If you're using this package in the context of the FCC on lxplus,
everything should be fine.
Any error message needs to be taken care of before going further. 


Environment
-----------

From this directory, run the initialization script, which makes a few
executable scripts available to you:

    source ./init.sh
    
Check that you can now import heppy:

    python
    import heppy 



Examples
--------

A simple example are provided in the test/ directory:

    cd test/

Create a root file with a tree:

    python create_tree.py
	
Process the root file:

    heppy_loop.py  Output   simple_example_cfg.py

Investigate the contents of the Output folder and its subdirectories. 
