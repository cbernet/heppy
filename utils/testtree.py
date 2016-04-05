from ROOT import TFile
from heppy.statistics.tree import Tree
import os

FNAME="test_tree.root"

def create_tree(filename=FNAME):
    if os.path.isfile(filename):
        return filename
    outfile = TFile(filename, 'recreate')
    tree = Tree('test_tree', 'A test tree')
    tree.var('var1')
    for i in range(200):
        tree.fill('var1', i)
        tree.tree.Fill()
    # print 'creating a tree', tree.tree.GetName(),\
    #    tree.tree.GetEntries(), 'entries in',\
    #    outfile.GetName()
    outfile.Write()
    outfile.Close()
    return outfile.GetName()

def remove_tree(filename=FNAME):
    os.remove(filename)
    
if __name__ == '__main__':
    create_tree()

