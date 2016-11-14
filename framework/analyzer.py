# Copyright (C) 2014 Colin Bernet
# https://github.com/cbernet/heppy/blob/master/LICENSE
"""Base Analyzer class. 
"""

import os
import sys
import logging

from heppy.statistics.counter import Counters
from heppy.statistics.average import Averages

class Analyzer(object):
    """Base Analyzer class. Used in L{Looper<looper.Looper>}.

    Your custom analyzers should inherit from this class, as done
    in this U{very simple example<https://github.com/HEP-FCC/heppy/blob/master/analyzers/examples/simple/RandomAnalyzer.py>}.
    
    An analyzer L{processes<process>} L{events<event.Event>}.
    The analyzer can read information from the L{event<event.Event>} by accessing the event data members::
    
      print event.iEv
      
    It can also add information to the L{event<event.Event>} by adding new attributes dynamically to the event
    object::
    
      event.the_variable = 0.03
      
    Each event is processed by a L{sequence<config.Sequence>} of analyzers in well-defined order.
    The information added to the event by a given analyzer can be used by subsequent analyzers. 
    
    Important attributes:
    
    @param cfg_ana: configuration parameters for this analyzer (e.g. to specify a pt cut).
    @param cfg_comp: configuration parameters for the data or MC component (e.g. DYJets).
    @param looperName: name of the L{Looper<looper.Looper>} which runs this analyzer.
    @param dirName: analyzer directory name, where you can write anything you want.
    @param verbose: boolean indicating whether the analyzer is in verbose mode.
    @param counters: dictionary of counters, empty by default.
    @param averages: dictionary of averages, empty by default.
    @param mainLogger: main logger, managed by the L{Looper<looper.Looper>} and common to all analyzers
    @param logger: logger specific to this analyzer. 
    """

    def __init__(self, cfg_ana, cfg_comp, looperName ):
        """Create an analyzer.
        
        Done by L{Looper<looper.Looper>} based on the contents of the heppy configuration file.

        @param cfg_ana: configuration parameters for this analyzer (e.g. to specify a pt cut)
        @param cfg_comp: configuration parameters for the data or MC component (e.g. DYJets)
        @param looperName: name of the L{Looper<looper.Looper>} which runs this analyzer.
        """
        self.class_object = cfg_ana.class_object
        self.instance_label = cfg_ana.instance_label
        self.name = cfg_ana.name
        self.verbose = cfg_ana.verbose
        self.cfg_ana = cfg_ana
        self.cfg_comp = cfg_comp
        self.looperName = looperName
        if hasattr(cfg_ana,"nosubdir") and cfg_ana.nosubdir:
            self.dirName = self.looperName
        else:
            self.dirName = '/'.join( [self.looperName, self.name] )
            os.mkdir( self.dirName )


        # this is the main logger corresponding to the looper.
        self.mainLogger = logging.getLogger( looperName )
        
        # this logger is specific to the analyzer
        self.logger = logging.getLogger(self.name)
        self.logger.addHandler(logging.FileHandler('/'.join([self.dirName,
                                                             'log.txt'])))
        self.logger.propagate = False
        self.logger.addHandler( logging.StreamHandler(sys.stdout) )
        log_level = logging.CRITICAL
        if hasattr(self.cfg_ana, 'log_level'):
            log_level = self.cfg_ana.log_level
        self.logger.setLevel(log_level)

        self.beginLoopCalled = False


    def beginLoop(self, setup):
        """Overload this method if you need to create objects or initialize variables
        at the beginning of the processing of the event sample.
       
        If you do so, make sure to execute this method::
        
          super(YourAnalyzerClass, self).beginLoop(setup) 
               
        Automatically called by L{Looper<looper.Looper>}, for all analyzers.        
        """
        self.counters = Counters()
        self.averages = Averages()
        self.mainLogger.info( 'beginLoop ' + self.cfg_ana.name )
        self.beginLoopCalled = True


    def endLoop(self, setup):
        """Overload this method if you need to perform tasks at the end of the processing.
        
        Files should be written or closed in L{write}, not here.  

        Automatically called by L{Looper<looper.Looper>}, for all analyzers.
        """
        #print self.cfg_ana
        self.mainLogger.info( '' )
        self.mainLogger.info( str(self) )
        self.mainLogger.info( '' )

    def process(self, event ):
        """Process event. 
        
        Each analyzer in the sequence is passed the same event object.
        Each analyzer can access, modify, and store event information, of any type.

        Automatically called by L{Looper<looper.Looper>}, for all analyzers.
        """
        print self.cfg_ana.name


    def write(self, setup):
        """Overload this method if you want to close or write files.
        
        If you do so, make sure to execute this method::
        
          super(YourAnalyzerClass, self).write(setup) 
        
        Automatically called by L{Looper<looper.Looper>}, for all analyzers.
        """
        self.counters.write( self.dirName )
        self.averages.write( self.dirName )
        if len(self.counters):
            self.logger.info(str(self.counters))
        if len(self.averages):
            self.logger.info(str(self.averages))
        

    def __str__(self):
        """A multipurpose printout. Should do the job for most analyzers."""
        ana = str( self.cfg_ana )
        count = ''
        ave = ''
        if hasattr(self, 'counters') and len( self.counters.counters ) > 0:
            count = '\n'.join(map(str, self.counters.counters))
        if hasattr(self, 'averages') and len( self.averages ) > 0:
            ave = '\n'.join(map(str, self.averages))
        return '\n'.join( [ana, count, ave] )
