import logging


'''
    Usage:
     Physics Debug output. Can write to file and/or to console. 
     is based on Python logging.
     
     To set it up
       import heppy.utils.pdebug as pdebugging
       from heppy.utils.pdebug import pdebugger
       
       
     Use following four lines and comment out as needed to obtain desired behaviour   
       #pdebugger.setLevel(logging.ERROR)  # turns off all output
       pdebugger.setLevel(logging.INFO) # turns on ouput
       pdebugging.set_file("pdebug.log",level=logging.INFO) #optional writes to file
       pdebugger.info("Run ee ZZ debug cfg")
       
    For example
     (1) file and console:
       pdebugger.setLevel(logging.INFO) 
       pdebugging.set_file("pdebug.log")
       
     (2) console only:
       pdebugger.setLevel(logging.INFO) 
       
     (3) file only:
       pdebugger.setLevel(logging.INFO)
       pdebugging.set_file("pdebug.log")
       pdebugging.set_streamlevel(logging.ERROR) 
    
     
     (4) no output 
       pdebugger.setLevel(logging.ERROR)
       or else no lines of code also gives same result
    
    to use in code
       from heppy.utils.pdebug import pdebugger
       pdebugger.info("A message")
    
'''


pdebugger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
pdebugger.addHandler(ch)

def set_file(filename = "pdebug.log", mode='w', level ="INFO"):
    #todo add checks
    cf = logging.FileHandler(filename, mode)
    cf.setLevel(level)
    pdebugger.addHandler(cf)

def set_streamlevel(level ="INFO"):
    ch.setLevel(level)


if __name__ == '__main__':
    logger = logging.getLogger('__main__')
    logger.warning('blah')
