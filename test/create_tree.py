from heppy.utils.testtree import create_tree

if __name__ == "__main__":
    
    import sys 
    if len(sys.argv) == 2: 
        nentries = sys.argv[1]
        create_tree(nentries=nentries) 
    else: 
        create_tree()
