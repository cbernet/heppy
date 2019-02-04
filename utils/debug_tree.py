'''Test tree management'''

from ROOT import TFile
from heppy.statistics.tree import Tree
import os

FNAME="test_tree.root"

def create_tree(filename=FNAME, nentries=None):
    '''Create the test tree in file FNAME.'''
    if not nentries:
        file_good = False
        if os.path.isfile(filename):
            rfile = TFile(filename)
            if not rfile.IsZombie():
                file_good = True
        if file_good:
            return filename
        else:
            # file needs to be regenerated so setting default
            # number of entries
            nentries = 200
    nentries = int(nentries)
    outfile = TFile(filename, 'recreate')
    tree = Tree('test_tree', 'A test tree')
    tree.var('var1')
    for i in range(nentries):
        tree.fill('var1', i)
        tree.tree.Fill()
    outfile.Write()
    outfile.Close()
    return outfile.GetName()

def remove_tree(filename=FNAME):
    '''Remove the test tree.'''
    os.remove(filename)
    
if __name__ == '__main__':
    create_tree()

