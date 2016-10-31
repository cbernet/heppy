An Example Analysis Workflow
============================

## FCC: ee &#8594; ZH &#8594; &mu;&mu; bb

This section shows an event processing sequence that could be used in a typical Higgs analysis on an electron-positron collider. 

The sequence is described in the configuration file [analysis_ee_ZH_cfg.py](../test/analysis_ee_ZH_cfg.py). 

This file and all python objects used therein are self-documented. To get more information on one of them, just import the file in python and use the python `help` function, e.g.,

```python
from analysis_ee_ZH_cfg import *
help(ResonanceBuilder)
```

