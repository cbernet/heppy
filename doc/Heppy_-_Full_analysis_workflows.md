# Full analysis workflows

This section presents heppy analysis sequences that are used in real experiments, present or future.

## Understanding heppy configuration files

All examples below are implemented in a specific configuration file like [analysis_ee_ZH_cfg.py](../test/analysis_ee_ZH_cfg.py).

These files are self documented, just open these files and read the inline comments.

To get more information on one of the objects used in these files, start `python` or `ipython` and use the python `help` function, e.g.,

```python
from analysis_ee_ZH_cfg import *
help(ResonanceBuilder)
```

```
Help on class ResonanceBuilder in module heppy.analyzers.ResonanceBuilder:

class ResonanceBuilder(heppy.framework.analyzer.Analyzer)
 |  Builds resonances.
 |
 |  Example:
 |
 |  from heppy.analyzers.ResonanceBuilder import ResonanceBuilder
 |  zeds = cfg.Analyzer(
 |    ResonanceBuilder,
 |    output = 'zeds',
 |    leg_collection = 'sel_iso_leptons',
 |    pdgid = 23
 |  )
 |
 |  * output : resonances are stored in this collection,
 |  sorted according to their distance to the nominal mass corresponding
 |  to the specified pdgid. The first resonance in this collection is thus the best one.
 |
 |  Additionally, a collection zeds_legs (in this case) is created to contain the
 |  legs of the best resonance.
 |
 |  * leg_collection : collection of particles that will be combined into resonances.
 |
 |  * pdgid : pythia code for the target resonance.
 |
 |  See Resonance2 and heppy.particles.tlv.Resonance for more information
 |
 |  Method resolution order:
 |      ResonanceBuilder
 |      heppy.framework.analyzer.Analyzer
 |      __builtin__.object
 |
 |  Methods defined here:
 |
 |  process(self, event)
 |
 |  ----------------------------------------------------------------------
 |  Methods inherited from heppy.framework.analyzer.Analyzer:
 |
 |  __init__(self, cfg_ana, cfg_comp, looperName)
 |      Create an analyzer.
 |
 |      Parameters (also stored as attributes for later use):
 |      cfg_ana: configuration parameters for this analyzer (e.g. a pt cut)
 |      cfg_comp: configuration parameters for the data or MC component (e.g. DYJets)
 |      looperName: name of the Looper which runs this analyzer.
 |
 |      Attributes:
 |      dirName : analyzer directory, where you can write anything you want
 |
 |  __str__(self)
 |      A multipurpose printout. Should do the job for most analyzers.
 |
 |  beginLoop(self, setup)
 |      Automatically called by Looper, for all analyzers.
 |
 |  endLoop(self, setup)
 |      Automatically called by Looper, for all analyzers.
 |
 |  write(self, setup)
 |      Called by Looper.write, for all analyzers.
 |      Just overload it if you have histograms to write.
 |
 |  ----------------------------------------------------------------------
 |  Data descriptors inherited from heppy.framework.analyzer.Analyzer:
 |
 |  __dict__
 |      dictionary for instance variables (if defined)
 |
 |  __weakref__
 |      list of weak references to the object (if defined)
```



## FCC: ee &#8594; ZH &#8594; &mu;&mu; bb

At the FCC-ee and at the ILC, Higgs bosons are produced through the ee &#8594; ZH process. The center-of-mass energy is set to 240 GeV. Signal events are selected by requiring two isolated muons. The mass of the two-muon system is required to be compatible with the Z mass. The Higgs four momentum is typically not reconstructed from the Higgs decay products, but as the difference between the initial p4 and the Z p4.
A given Higgs decay channel can be selected by identifying the particles present in the final state in addition to the two muons, e.g.  b jets or &tau; leptons.

The sequence is described in the configuration file [analysis_ee_ZH_cfg.py](../test/analysis_ee_ZH_cfg.py). It consists in the following steps:

*Simulation and reconstruction:*

1. read generated particles from an FCC-ee event sample
1. run the stable gen particles through a simulation of the CMS detector in [papas](papas_-_The_PArametrized_PArticle_Simulation.md).

*Analysis:*

1. select leptons of a given type (either electron or muon)
1. compute lepton isolation
1. select isolated leptons
1. build Z candidates from the list of selected leptons, and choose the Z with the mass closest to mZ.
1. compute the four-momentum of the particles recoiling against the Z.
1. compute the missing four-momentum.
1. remove the leptons corresponding to the selected Z from the list of particules, and reconstruct two exclusive jets
1. build a higgs candidate from the two jets
1. fill a simple cut-flow table
1. fill a tree (ntuple)

## FCC-hh pp &#8594; H &#8594; 4 leptons

To be written.

## FCC-hh pp &#8594; t tbar

To be written
