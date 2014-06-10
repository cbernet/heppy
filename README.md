TLEP
====

Prerequisites 
-------------

* python 2.x, x>5
* ROOT 5


Environment
-----------

From this directory, run the initialization script:
	
	source init.sh


Examples
--------

Several examples are provided in the test/ directory:
	cd test/
	
Read a root file and print each event:
	multiloop.py  Trash   print_events_cfg.py

Read a root file and create a simple tree:
	multiloop.py  Trash2  simple_tree_cfg.py

Todo list
---------

* TODO organize subdirs / review dependencies
* TODO run pylint
  * make all modules lower case.
* TODO add unittests whenever possible
  * tests in same dir
  * how to organize global test suite?
