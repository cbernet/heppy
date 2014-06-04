from ROOT import TFile
from statistics.TreeNumpy import TreeNumpy

#TODO create CWN

outfile = TFile('test_tree.root', 'recreate')
tree = TreeNumpy('test_tree', 'A test tree')
tree.var('var1')

for i in range(1000):
    tree.fill('var1', i)
    tree.tree.Fill()

print 'creating a tree with', tree.tree.GetEntries(), 'entries in',\
      outfile.GetName()

outfile.Write()
