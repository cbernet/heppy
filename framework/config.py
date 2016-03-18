# Copyright (C) 2014 Colin Bernet
# https://github.com/cbernet/heppy/blob/master/LICENSE

from weight import Weight
import glob

# Forbidding PyROOT to hijack help system,
# in case the configuration module is used as a script.
import ROOT 
ROOT.PyConfig.IgnoreCommandLineOptions = True

def printComps(comps, details=False):
    '''
    Summary printout for  a list of components comps.
    The components are assumed to have a name, and a list of files,
    like the ones from this module.
    '''
    nJobs = 0
    nCompsWithFiles = 0
    for c in comps:
        if not hasattr(c, 'splitFactor'):
            c.splitFactor = 1
        print c.name, c.splitFactor, len(c.files)
        if len(c.files)==0:
            continue
        else:
            if details:
                print c.files[0]
            nJobs += c.splitFactor
            nCompsWithFiles += 1

    print '-'*70
    print '# components with files = ', nCompsWithFiles
    print '# jobs                  = ', nJobs


class CFG(object):
    '''Base configuration class. The attributes are used to store parameters of any type'''
    def __init__(self, **kwargs):
        '''All keyword arguments are added as attributes.'''
        self.__dict__.update( **kwargs )

    def __str__(self):
        '''A useful printout'''
        header = '{type}: {name}'.format( type=self.__class__.__name__,
                                          name=self.name)
        varlines = ['\t{var:<15}:   {value}'.format(var=var, value=value) \
                    for var,value in sorted(vars(self).iteritems()) \
                    if var is not 'name']
        all = [ header ]
        all.extend(varlines)
        return '\n'.join( all )
    
class Analyzer( CFG ):
    '''Base analyzer configuration, see constructor'''
    names = set()
    
    def __init__(self, class_object, instance_label='1', 
                 verbose=False, **kwargs):
        '''
        One could for example define the analyzer configuration for a
        di-muon framework.Analyzer.Analyzer in the following way:

        ZMuMuAna = cfg.Analyzer(
          ZMuMuAnalyzer,
          'zmumu', # optional!
          pt1 = 20,
          pt2 = 20,
          iso1 = 0.1,
          iso2 = 0.1,
          eta1 = 2,
          eta2 = 2,
          m_min = 0,
          m_max = 200
        )

        The first argument is your analyzer class. 
        It should inherit from heppy.framework.analyzer.Analyser 

        The second argument is optional.
        If you have several analyzers of the same class, 
        e.g. ZEleEleAna and ZMuMuAna, 
        you may choose to provide it to keep track of the output 
        of these analyzers. 
        If you don't so so, the instance labels of the analyzers will
        automatically be set to 1, 2, etc.

        Finally, any kinds of keyword arguments can be added.
        
        This analyzer configuration object will become available 
        as self.cfg_ana in your ZMuMuAnalyzer.
        '''

        self.class_object = class_object
        self.instance_label = instance_label
        self.verbose = verbose
        super(Analyzer, self).__init__(**kwargs)

    def __setattr__(self, name, value):
        '''You may decide to copy an existing analyzer and change
        its instance_label. In that case, one must stay consistent.'''
        self.__dict__[name] = value
        if name == 'instance_label':
            self.name = self._build_name()   

    def _build_name(self):
        class_name = '.'.join([self.class_object.__module__, 
                               self.class_object.__name__])
        while 1:
            # if class_name == 'heppy.analyzers.ResonanceBuilder.ResonanceBuilder':
            #    import pdb; pdb.set_trace()
            name = '_'.join([class_name, self.instance_label])
            if name not in self.__class__.names:
                self.__class__.names.add(name)
                break
            else:
                # cannot set attr directly or infinite recursion,
                # see setattr
                iinst = None
                try:
                    iinst = int(self.instance_label)
                    self.__dict__['instance_label'] = str(iinst+1)
                except ValueError:
                    # here, reloading module in ipython
                    self.__class__.names = set()
                    self.__dict__['instance_label'] = self.instance_label
        return name 

    
class Service( CFG ):
    
    def __init__(self, class_object, instance_label='1', 
                 verbose=False, **kwargs):
        self.class_object = class_object
        self.instance_label = instance_label
        self.name = self._build_name()
        self.verbose = verbose
        super(Service, self).__init__(**kwargs)

    def _build_name(self):
        class_name = '.'.join([self.class_object.__module__, 
                               self.class_object.__name__])
        name = '_'.join([class_name, self.instance_label])
        return name 
   

class Sequence( list ):
    '''A list with print functionalities.

    Used to define a sequence of analyzers.'''
    def __str__(self):
        tmp = []
        for index, ana in enumerate( self ):
            tmp.append( '{index} :'.format(index=index) )
            tmp.append( '{ana} :'.format(ana=ana) )
        return '\n'.join(tmp)

#TODO review inheritance, and in particular constructor args - this is a mess.

class Component( CFG ):
    '''Base component class.

    See the child classes:
    DataComponent, MCComponent, EmbedComponent
    for more information.'''
    def __init__(self, name, files, tree_name=None, triggers=None, **kwargs):
        if isinstance(triggers, basestring):
            triggers = [triggers]
        super( Component, self).__init__( name = name,
                                          files = files,
                                          tree_name = tree_name,
                                          triggers = triggers, **kwargs)
        self.dataset_entries = 0
        self.isData = False
        self.isMC = False
        self.isEmbed = False

class DataComponent( Component ):

    def __init__(self, name, files, intLumi=None, triggers=[], json=None):
        super(DataComponent, self).__init__(name, files, triggers=triggers)
        self.isData = True
        self.intLumi = intLumi
        self.json = json

    def getWeight( self, intLumi = None):
        return Weight( genNEvents = -1,
                       xSection = None,
                       genEff = -1,
                       intLumi = self.intLumi,
                       addWeight = 1. )



class MCComponent( Component ):
    def __init__(self, name, files, triggers=[], xSection=1,
                 nGenEvents=None,
                 effCorrFactor=None, **kwargs ):
        super( MCComponent, self).__init__( name = name,
                                            files = files,
                                            triggers = triggers, **kwargs )
        self.xSection = xSection
        self.nGenEvents = nGenEvents
        self.effCorrFactor = effCorrFactor
        self.isMC = True
        self.intLumi = 1.
        self.addWeight = 1.

    def getWeight( self, intLumi = None):
        # if intLumi is None:
        #    intLumi = Weight.FBINV
        #COLIN THIS WEIGHT STUFF IS REALLY BAD!!
        # use the existing Weight class or not? guess so...
        return Weight( genNEvents = self.nGenEvents,
                       xSection = self.xSection,
                       intLumi = self.intLumi,
                       genEff = 1/self.effCorrFactor,
                       addWeight = self.addWeight )

class Config( object ):
    '''Main configuration object, holds a sequence of analyzers, and
    a list of components.'''
    def __init__(self, components, sequence, services, events_class,preprocessor=None):
        self.preprocessor = preprocessor
        self.components = components
        self.sequence = sequence
        self.services = services
        self.events_class = events_class

    def __str__(self):
        comp = '\n'.join(map(str, self.components))
        sequence = str(self.sequence)
        services = '\n'.join( map(str, self.services))
        return '\n'.join([comp, sequence, services])


