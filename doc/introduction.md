# Heppy: Introduction

Heppy (High Energy Physics with PYthon) is a modular python framework for the analysis of collision events.

Why python? 

* fast learning curve: python is the most easy-to-learn language
* high productivity: coding in python is about 10 times faster than in C++
* high flexibility: code can be easily reused, refactored, extended.
* dynamic typing (similar to C++ template features, without the pain in the neck): if you do an analysis for e.g. the muon channel, it is going to work for the electron channel with only minor modifications related to lepton identification. If your analysis reads a certain kind of particle-like objects, it will probably work on other kinds of particle-like objects.
* very large and easy-to-use standard library 

This goal of the ntuplizer system is to produce a flat tree for each of the datasets (also called "components") used in the analysis. Any operation requiring a manual loop on the events can be done while producing the flat tree, so that the resulting trees can be used with simple TTree.Draw or TTree.Project commands.

For example, the ntuplizer allows to:

* read events from an EDM root file, e.g. mini AODs.
* create python physics objects wrapping the C++ objects from the EDM root file. These objects have the exact same interface as the C++ objects, and can be extended with more information. For example, you could write your own muon ID function for your python Muon object, or add attributes to your python Muons along the processing flow, like the 4-momentum of the closest jet or the closest generated muon.
* create new python objects, e.g. a VBF object to hold VBF quantities.
compute event-by-event weights
* select a trigger path, and match to the corresponding trigger objects
* define and write simple flat trees 

It is up to you to define what you want to do, possibly re-using existing code from other analyses or writing your own.

An analysis typically consists in several tenth of samples, or "components": data samples, standard model backgrounds, signal. The ntuplizer is built in such a way that it takes one command to either:

* run interactively on a single component
* run several processes in parallel on your multiprocessor machine
* run hundreds of processes as separate jobs on LSF, the CERN batch cluster. 

If you decide to run several processes, you can split a single component in as many chunks as input ROOT files for this component. For example, you could run in parallel:

* 6 chunks from the DYJet component, using 6 processors of your local machine, assuming you have more than 6 input DYJet ROOT files.
* 200 chunks from the DYJet component, 300 from your 5 data components altogether, and 300 jobs from all the remaing components (e.g. di-boson, TTJets, ...) on LSF. 

The ntuplizer is based on python, pyroot, and FWLite. The analysis could be a simple python macro based on these tools. Instead, it was decided to keep the design of typical full frameworks for high-energy physics (e.g. CMS, ATLAS, FCC), and to implement it in python. This design boils down to:

* a python configuration system, similar to the one we use in HEP full frameworks like CMSSW.
* a Looper which allows to access the EDM events and runs a sequence of analyzers on each event.
* a common python event, created at the beginning of the processing of each EDM event, and read/modified by the analyzers. 

the python event allows you to build the information you want into your event, and allows the analyzers to communicate. At the end of the processing of a given EDM event, information from the python event can be filled into a flat tree using a specific kind of analyzer, like this one.

