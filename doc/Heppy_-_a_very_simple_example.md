# A very simple heppy example

Contents:

  * [A very simple heppy example](#a-very-simple-heppy-example)
    * [Running the example](#running-the-example)
    * [Using python to inspect and modify the configuration](#using-python-to-inspect-and-modify-the-configuration)
    * [Configuration file structure](#configuration-file-structure)
      * [Importing a few useful modules](#importing-a-few-useful-modules)
      * [Definition of the input events](#definition-of-the-input-events)
      * [Configuration of the analyzers](#configuration-of-the-analyzers)
      * [Scheduling of the event processing sequence](#scheduling-of-the-event-processing-sequence)
      * [Definition of global services](#definition-of-global-services)
      * [finalization of the configuration object](#finalization-of-the-configuration-object)

A [simple heppy example](../test/simple_example_cfg.py) based on ROOT is provided in the test/ directory.

## Running the example

Please do the following:

```bash
    cd test/
    # create a root file containing an example root tree:
    python create_tree.py
	 # process this tree:
    heppy_loop.py  Output/ simple_example_cfg.py
```

The two arguments are:

* Output/ : The output directory in which the results are stored
* [simple_example_cfg.py](../test/simple_example_cfg.py) : heppy configuration file

**Inspection of the ouput**

## Using python to inspect and modify the configuration

Heppy configuration files like [simple_example_cfg.py](../test/simple_example_cfg.py) are just python modules that can be imported and used in python.

Start python (here we use the superior ipython script):

    ipython

import the [simple_example_cfg.py](../test/simple_example_cfg.py) module:

```python
from heppy.test.simple_example_cfg import *
```

you can now use the various python objects in cfg_file, e.g. to get help:

```python
help(Events)
```

```
Help on class Chain in module heppy.framework.chain:

class Chain(__builtin__.object)
 |  Wrapper to TChain, with a python iterable interface.
 |
 |  from chain import Chain
 |  the_chain = Chain('../test/test_*.root', 'test_tree')
 |  event3 = the_chain[2]
 |  print event3.var1
 |
 |  for event in the_chain:
 |      print event.var1
 |
 |  Methods defined here:
 |
 |  __getattr__(self, attr)
 |      All functions of the wrapped TChain are made available
 |
 |  __getitem__(self, index)
 |      Returns the event at position index.
 |
 |  __init__(self, input_filenames, tree_name=None)
 |      Create a chain.
 |
 |      Parameters:
 |        input     = either a list of files or a wildcard (e.g. 'subdir/*.root').
 |                    In the latter case all files matching the pattern will be used
 |                    to build the chain.
 |        tree_name = key of the tree in each file.
 |                    if None and if each file contains only one TTree,
 |                    this TTree is used.
 |
 |  __iter__(self)
 |
 |  __len__(self)
 |
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |
 |  __dict__
 |      dictionary for instance variables (if defined)
 |
 |  __weakref__
 |      list of weak references to the object (if defined)
```

It is possible to access the attributes and the methods of the various objects, and for example to print them:

```python
print inputSample
```
```
Component: test_component
        dataset_entries:   0
        files          :   ['/Users/cbernet/Code/FCC/heppy/doc/test_tree.root']
        isData         :   False
        isEmbed        :   False
        isMC           :   False
        tree_name      :   None
        triggers       :   None
```

It is even possible to use all functionalities of python to prepare your heppy configuration file. For example to use all ROOT files in the current directory as input, one could add the following lines to the configuration file. You may run them now:

```python
import glob
files = glob.glob('*.root')
inputSample.files = files
print files
```

## Configuration file structure

The goal of the heppy configuration file is to:

* specify the input samples of events
* configure the analyzers responsible for event processing
* schedule the event processing sequence
* gather all of this information in a configuration object for hepp

These steps are described for [simple_example_cfg.py](../test/simple_example_cfg.py), which is reproduced below.

### Importing a few useful modules

```python
import os
import heppy.framework.config as cfg
import logging
logging.basicConfig(level=logging.INFO)
```

### Definition of the input events

```python

# input component
# several input components can be declared,
# and added to the list of selected components

inputSample = cfg.Component(
    'test_component',
    # create the test file by running
    # python create_tree.py
    files = [os.path.abspath('test_tree.root')],
    )

selectedComponents  = [inputSample]

# use a simple event reader based on the ROOT TChain class
from heppy.framework.chain import Chain as Events
```

In this example, we read a single root file using the ROOT TChain class.

One could read a list of files, and even have several input samples (or components), each with its own list of files. Heppy offers the possibility to [process all files of all components in parallel](Heppy_-_Parallel_Processing.md), with a single command.

The Events class here stands for a Chain, which wraps a TChain. It is responsible for reading the events written in the component files. Specific Events classes are provided to read [CMS](../framework/eventsfwlite.py), [FCC](https://github.com/HEP-FCC/podio/blob/master/python/EventStore.py), and [LCIO](../framework/eventslcio.py) events.
Other Events classes could be provided e.g for ATLAS events or plain text files such as Les Houches or HepMC events.

### Configuration of the analyzers

This section of the configuration file specifies the configuration of four very simple analyzers:

* [RandomAnalyzer](../analyzers/examples/simple/RandomAnalyzer.py) : draw a value from a random distribution for a variable and put it into the event.
* [Printer](../analyzers/examples/simple/Printer.py) : access this variable and print it.
* [Stopper](../analyzers/examples/simple/Stopper.py) : stop processing at event 10.
* [SimpleTreeProducer](../analyzers/examples/simple/SimpleTreeProducer.py): define an output ntuple (TTree) to store the random variable.

Please study the sequence below, and the code of each analyzer.

```python

# add a random variable to the event
from heppy.analyzers.examples.simple.RandomAnalyzer import RandomAnalyzer
random = cfg.Analyzer(
    RandomAnalyzer
    )

# just print a variable in the input test tree
from heppy.analyzers.examples.simple.Printer import Printer
printer = cfg.Analyzer(
    Printer,
    log_level=logging.INFO
    )

# illustrates how to use an exception to stop processing at event 10
# for debugging purposes.
from heppy.analyzers.examples.simple.Stopper import Stopper
stopper = cfg.Analyzer(
    Stopper,
    iEv = 10
    )

# creating a simple output tree
from heppy.analyzers.examples.simple.SimpleTreeProducer import SimpleTreeProducer
tree = cfg.Analyzer(
    SimpleTreeProducer,
    tree_name = 'tree',
    tree_title = 'A test tree'
    )
```


### Scheduling of the event processing sequence

The following lines define which analyzers will run, and in which order they will process each event. The `printer` and the `stopper` are left out from the sequence on purpose. The analyzer `random` runs first so that the resulting random variable can be stored in the ntuple by `tree` later on.

```python
# definition of a sequence of analyzers,
# the analyzers will process each event in this order
sequence = cfg.Sequence([
        random,
        # printer,
        # stopper,
        tree,
] )
```

Please include `printer` and `stopper` to the sequence, and run again.

### Definition of global services

_Services_ are created at the beginning of the event processing and can be used in all analyzers. They are usually not needed but are worth mentioning. For example, the service defined below configures a global output root file that can be used by all analyzers. Please note however that each analyzer can also have its own output ROOT file.

```python
from heppy.framework.services.tfile import TFileService
output_rootfile = cfg.Service(
    TFileService,
    'myhists',
    fname='histograms.root',
    option='recreate'
)

services = [output_rootfile]
```

### finalization of the configuration object

A global configuration file named `config` must be present. It contains all the information needed by heppy to process your events.

```python
# finalization of the configuration object.
config = cfg.Config( components = selectedComponents,
                     sequence = sequence,
                     services = services,
                     events_class = Events )

# print config
```



/
