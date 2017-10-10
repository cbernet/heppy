import modulefinder
import git
import yaml
import sys
import fnmatch
import pprint

########################################################################
class Versions(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, scriptfname, to_track):
        """Analyze the script scriptfname to find the version of the
        packages matching the patterns in to_track
        """
        # remove standard python2 path to speed things up
        exclude = 'python2'
        path = [p for p in sys.path if 'python2' not in p]
        self.scriptfname = scriptfname
        self.finder = modulefinder.ModuleFinder(path)
        self.finder.run_script(scriptfname)
        # self.finder.report()
        self.tracked = dict()
        for key, mod in self.finder.modules.iteritems():
            for pattern in to_track:
                if fnmatch.fnmatch(key, pattern):
                    self._analyze(key, mod)
                    break
        
    def _analyze(self, key, module):
        info = dict()
        repo = git.Repo(module.__path__[0])
        info['commitid'] = repo.head.commit.hexsha
        self.tracked[key] = info
        print

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
    
