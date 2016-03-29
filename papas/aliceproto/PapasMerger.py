class ClusterMerger(object):

    def __init__(self,clusters,ruler):
        ''' Simple check that two sets of sensible sorted particles are the same
            will stop on an assert if things are different
            assumes particles are ordered in the same way
            is relatively naive but sufficient so far
        '''
def merge_clusters(clusters, layer):
    merged = []
    
    links = Links(clusters,layer, distance)
    for group in links.groups.values():
        if len(group) == 1:
            merged.append(group[0]) 
            continue
        supercluster = None
        for cluster in group: 
            if supercluster is None:
                supercluster = copy.copy(cluster)
                merged.append(supercluster)
                continue
            else: 
                supercluster += cluster
    merged.extend(elem_other)
    return merged