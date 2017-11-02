import modulefinder
import git
import yaml
import sys
import os
import fnmatch
import pprint

########################################################################
class Versions(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, scriptfname):
        """Analyze the script scriptfname to find the version of the
        packages matching the patterns in to_track
        """
        # remove standard python2 path to speed things up
        exclude = 'python2'
        path = [p for p in sys.path if 'python2' not in p]
        self.scriptfname = scriptfname
        finder = modulefinder.ModuleFinder(path)
        finder.run_script(scriptfname)
#        finder.report()
        self.tracked = dict()
        processed = []
        for key, mod in finder.modules.iteritems():
            #if mod.__path__ and os.environ['USER'] in mod.__path__[0]:
            self._analyze(key, mod)

    def _analyze(self, key, module):
        info = dict()
        if module.__path__:
            try:        
                repo = git.Repo(module.__path__[0])
                info['commitid'] = repo.head.commit.hexsha
                self.tracked[key] = info
            except git.InvalidGitRepositoryError:
                pass 

    #----------------------------------------------------------------------
    def write_yaml(self, path):
        '''write the versions to a yaml file'''
        data = dict(software=dict())
        # now only one information, the commit id.
        # so simplifying the dictionary structure
        for package, info in self.tracked.iteritems():
            data['software'][package] = info['commitid']
        with open(path, mode='w') as outfile:
                yaml.dump(data, outfile,
                          default_flow_style=False)    
    
    def __str__(self):
        return pprint.pformat(self.tracked)
    
