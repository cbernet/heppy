# Heppy : Installation Instructions 

heppy can be used to read any type of input file, and in particular: 

* text files or python formats (pickle, hf5, etc)
* ROOT files 
* EDM files from the CMS, ILC/CLIC, or FCC experiments

If you only intend to read files readable in python, possibly with additional python libraries, the bare installation is for you. 

If you need to read ROOT files, refer to the ROOT-based installation.

If you belong to CMS, ILC/CLIC, or FCC, please refer to the instructions provided by these experiments. 


## Basic installation 

heppy requires python 2.7.X, and is not compatible with python 3 yet. 

You can install this version of python manually, or get it through [Anaconda](https://www.anaconda.com/).

If you choose to use Anaconda, first [download it](https://www.anaconda.com/distribution/) (pick the 2.X version) and install it.

Then, create an environment for heppy: 

```
conda create -n heppy python=2.7
conda activate heppy
```

And finally install heppy: 

```
pip install heppyfwk
```

To test your installation, you can download the configuration file [text\_example\_cfg.py](https://raw.githubusercontent.com/cbernet/heppy/master/test/text_example_cfg.py) and do 

```
heppy Out text_example_cfg.py
```

You should get an output like: 

```
starting loop at event 0 to process 100 events.
Component: test_component
        dataset_entries:   0
        files          :   ['/var/folders/tf/xx9nk7w1511c4l0xd95pmpdw0002cy/T/tmpQRQ1hO']
        isData         :   False
        isEmbed        :   False
        isMC           :   False
        tree_name      :   None
        triggers       :   None
beginLoop heppy.analyzers.examples.simple.TextAnalyzer.TextAnalyzer_1
event 0
Event: 0
{   'analyzers': [   (   heppy.analyzers.examples.simple.TextAnalyzer.TextAnalyzer_1,
                         True)],
    'eventWeight': 1,
    'iEv': 0,
    'x1': 0,
    'x2': 0}
Event: 1
{   'analyzers': [   (   heppy.analyzers.examples.simple.TextAnalyzer.TextAnalyzer_1,
                         True)],
    'eventWeight': 1,
    'iEv': 1,
    'x1': 1,
    'x2': 1}
Event: 2
{   'analyzers': [   (   heppy.analyzers.examples.simple.TextAnalyzer.TextAnalyzer_1,
                         True)],
    'eventWeight': 1,
    'iEv': 2,
    'x1': 2,
    'x2': 4}
Event: 3
{   'analyzers': [   (   heppy.analyzers.examples.simple.TextAnalyzer.TextAnalyzer_1,
                         True)],
    'eventWeight': 1,
    'iEv': 3,
    'x1': 3,
    'x2': 9}
Event: 4
{   'analyzers': [   (   heppy.analyzers.examples.simple.TextAnalyzer.TextAnalyzer_1,
                         True)],
    'eventWeight': 1,
    'iEv': 4,
    'x1': 4,
    'x2': 16}

Analyzer: heppy.analyzers.examples.simple.TextAnalyzer.TextAnalyzer_1
        class_object   :   <class 'heppy.analyzers.examples.simple.TextAnalyzer.TextAnalyzer'>
        instance_label :   1
        verbose        :   False


Component: test_component
        dataset_entries:   0
        files          :   ['/var/folders/tf/xx9nk7w1511c4l0xd95pmpdw0002cy/T/tmpQRQ1hO']
        isData         :   False
        isEmbed        :   False
        isMC           :   False
        tree_name      :   None
        triggers       :   None


      ---- TimeReport (all times in ms; first evt is skipped) ---- 
processed    all evts    time/proc    time/all   [%]    analyer
---------    --------    ---------   ---------  -----   -------------
      100         100         0.00        0.00 100.0%   heppy.analyzers.examples.simple.TextAnalyzer.TextAnalyzer_1
---------    --------    ---------   ---------   -------------
      100         100         0.00        0.00 100.0%   TOTAL

Counter analyzers :
         heppy.analyzers.examples.simple.TextAnalyzer.TextAnalyzer_1            100      1.00    1.0000

number of events processed: 100
(heppy_test_pypi) [~]$ ls Out/test_component/        
__cfg_to_run__.py                                           log.txt
component.pck                                               software.yaml
config.pck                                                  text_cfg.py
```

## ROOT-based installation

First, follow the basic installation instructions just above. 

**Absolutely make sure that your conda environment is activated if you use anaconda.**

To use heppy with ROOT, it is necessary to compile ROOT with the same version of python as used in heppy. 

So please do the following to check that your version of python is the one you expect: 

```
which python
python --version
```

To compile ROOT, we need `cmake`. On mac OS, you can install it easily with [homebrew](https://brew.sh/) by doing: 

```
brew install cmake
```

To download ROOT: 

* go to [https://root.cern.ch/downloading-root]()
* select the Pro release (6.16/00 at the time of this writing)
* download the source distribution

Please check [these instructions](https://root.cern.ch/building-root) before attempting to build ROOT. 

But these instructions can be a bit complicated, so here are the steps I followed: 

```
tar -zxvf root_v6.16.00.source.tar.gz
cd root-6.16.00
mkdir my_build
cd my_build
cmake .. 
```

cmake will perform a number of tests. Then compile:

```
make -j 4 
```

After compilation, you can test do basic tests: 

* test that ROOT can be executed 

```
source bin/thisroot.sh 
root -l 
```

* try to import ROOT from python (which heppy does a lot): 

```
python 
import ROOT 
```

This should give **no error and not message whatsoever.** If there is an issue importing ROOT, you need to sort it out before going further. It could be that a different version of python was picked when you compiled ROOT. 

When you're sure everything is fine, you can install ROOT in its destination place (sudo is necessary to have the rights to write to the default destination place, `/usr/local`) 

```
sudo make install 
```

Finally, add the following to your `.bash_profile` (replace the root destination if you don't use the default one): 

```
source /usr/local/bin/thisroot.sh
```

Now, let's run a small root test.

For that, we need to create a simple test tree. Fire up python and do: 

```
from heppy.utils.debug_tree import create_tree
create_tree()
```

Leave python, open the resulting root file with root, and check the contents of the tree. 

Now, download the configuration file [simple\_example\_cfg.py](https://raw.githubusercontent.com/cbernet/heppy/master/test/simple_example_cfg.py) and do 

```
heppy OutRoot simple_example_cfg.py
```

You should get such an output: 

```
starting loop at event 0 to process 200 events.
Component: test_component
        dataset_entries:   0
        files          :   ['/Users/cbernet/test_tree.root']
        isData         :   False
        isEmbed        :   False
        isMC           :   False
        tree_name      :   None
        triggers       :   None
beginLoop heppy.analyzers.examples.simple.RandomAnalyzer.RandomAnalyzer_1
beginLoop heppy.analyzers.examples.simple.SimpleTreeProducer.SimpleTreeProducer_1
event 0
Event: 0
{   'analyzers': [   (   heppy.analyzers.examples.simple.RandomAnalyzer.RandomAnalyzer_1,
                         True),
                     (   heppy.analyzers.examples.simple.SimpleTreeProducer.SimpleTreeProducer_1,
                         True)],
    'eventWeight': 1,
    'iEv': 0,
    'var_random': 0.1543001532554629}
Event: 1
{   'analyzers': [   (   heppy.analyzers.examples.simple.RandomAnalyzer.RandomAnalyzer_1,
                         True),
                     (   heppy.analyzers.examples.simple.SimpleTreeProducer.SimpleTreeProducer_1,
                         True)],
    'eventWeight': 1,
    'iEv': 1,
    'var_random': 0.42324515851214595}
Event: 2
{   'analyzers': [   (   heppy.analyzers.examples.simple.RandomAnalyzer.RandomAnalyzer_1,
                         True),
                     (   heppy.analyzers.examples.simple.SimpleTreeProducer.SimpleTreeProducer_1,
                         True)],
    'eventWeight': 1,
    'iEv': 2,
    'var_random': 0.7905995836481464}
Event: 3
{   'analyzers': [   (   heppy.analyzers.examples.simple.RandomAnalyzer.RandomAnalyzer_1,
                         True),
                     (   heppy.analyzers.examples.simple.SimpleTreeProducer.SimpleTreeProducer_1,
                         True)],
    'eventWeight': 1,
    'iEv': 3,
    'var_random': 0.24638669146224895}
Event: 4
{   'analyzers': [   (   heppy.analyzers.examples.simple.RandomAnalyzer.RandomAnalyzer_1,
                         True),
                     (   heppy.analyzers.examples.simple.SimpleTreeProducer.SimpleTreeProducer_1,
                         True)],
    'eventWeight': 1,
    'iEv': 4,
    'var_random': 0.19370838068425686}
event 100 (5020.8 ev/s)

Analyzer: heppy.analyzers.examples.simple.RandomAnalyzer.RandomAnalyzer_1
        class_object   :   <class 'heppy.analyzers.examples.simple.RandomAnalyzer.RandomAnalyzer'>
        instance_label :   1
        verbose        :   False


Analyzer: heppy.analyzers.examples.simple.SimpleTreeProducer.SimpleTreeProducer_1
        class_object   :   <class 'heppy.analyzers.examples.simple.SimpleTreeProducer.SimpleTreeProducer'>
        instance_label :   1
        tree_name      :   tree
        tree_title     :   A test tree
        verbose        :   False


Component: test_component
        dataset_entries:   0
        files          :   ['/Users/cbernet/test_tree.root']
        isData         :   False
        isEmbed        :   False
        isMC           :   False
        tree_name      :   None
        triggers       :   None


      ---- TimeReport (all times in ms; first evt is skipped) ---- 
processed    all evts    time/proc    time/all   [%]    analyer
---------    --------    ---------   ---------  -----   -------------
      200         200         0.02        0.02  37.6%   heppy.analyzers.examples.simple.RandomAnalyzer.RandomAnalyzer_1
      200         200         0.03        0.03  62.4%   heppy.analyzers.examples.simple.SimpleTreeProducer.SimpleTreeProducer_1
---------    --------    ---------   ---------   -------------
      200         200         0.05        0.05 100.0%   TOTAL

Counter analyzers :
         heppy.analyzers.examples.simple.RandomAnalyzer.RandomAnalyzer_1                    200          1.00    1.0000
         heppy.analyzers.examples.simple.SimpleTreeProducer.SimpleTreeProducer_1            200          1.00    1.0000
```

This configuration defines a process that: 

* reads the tree, 
* adds a random value to the event
* creates an output tree with: 
	* the variable that is in the input tree
	* the random variable

You can find the output tree in: 

```
OutRoot/test_component/heppy.analyzers.examples.simple.SimpleTreeProducer.SimpleTreeProducer_1/simple_tree.root
```	