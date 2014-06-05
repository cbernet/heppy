from ROOT import TFile
from statistics.TreeNumpy import TreeNumpy

#TODO create CWN

outfile = TFile('test_tree.root', 'recreate')

tree = TreeNumpy('test_tree', 'A test tree')
tree.var('var1')

tree2 = TreeNumpy('test_tree_2', 'Another test tree')
tree2.var('var2')

for i in range(100):
    tree.fill('var1', i)
    tree.tree.Fill()
    tree2.fill('var2', 2*i)
    tree2.tree.Fill()

print 'creating a tree', tree.tree.GetName(),\
      tree.tree.GetEntries(), 'entries in',\
      outfile.GetName()
print 'creating a tree with', tree2.tree.GetName(),\
      tree2.tree.GetEntries(), 'entries in',\
      outfile.GetName()

outfile.Write()
