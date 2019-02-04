#todo make depend on Heppy Configuration
from heppy.framework.context import name

if name == 'bare': # ROOT not here
    from random import *
else: # ROOT here in cms and fcc contexts
    from random_root import *

# not used:
#from random_cpplib import *
