# Heppy : Installation Instructions 

heppy can be used to read any type of input file, and in particular: 

* text files 
* python formats (pickle, hf5, etc)
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