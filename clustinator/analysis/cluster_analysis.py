'''
@author: An Dang, Henning Schulz
'''

import numpy as np
from collections import defaultdict
from itertools import product

old_min_points = {}
cluster_mean_history = {}
min_point_label_list = []

class Cluster_analysis:

    def __init__(self, prev_means, new_means):
        self.prev_means = prev_means
        self.new_means = new_means
    
    def cluster_mapping(self):
        """
        Calculates the mapping of cluster labels in the new clustering to labels in the previous clustering
        :return: dict { new cluster label -> previous cluster label }
        """
        mapping = {}
        
        comparison = []

        for prev, new in product(self.prev_means.keys(), self.new_means.keys()):
            diff = np.linalg.norm(np.asarray(self.prev_means[prev]) - np.asarray(self.new_means[new]))
            comparison.append((prev, new, diff))
        
        comparison.sort(key = lambda tup: tup[2])
        prev_mapped = []
        new_mapped = []
        
        for tup in comparison:
            if (tup[0] not in prev_mapped) and (tup[1] not in new_mapped):
                print('  mapping (new %r -> prev %r): diff %r' % (tup[1], tup[0], tup[2]))
                mapping[tup[1]] = tup[0]
                prev_mapped.append(tup[0])
                new_mapped.append(tup[1])
        
        unmapped = [label for label in self.new_means if label not in new_mapped]
        
        for label in unmapped:
            mapping[label] = label
        
        return mapping
    
    def relabel_clusters(self, cluster_mapping_dict):
        """
        Relabels the clusters based on the provided mapping.
        :param cluster_mapping_dict: The mapping of new to previous cluster labels
        :return: dict { previous cluster label -> mean markov chain } 
        """
        
        remapped_clusters = {}
        
        for key, value in self.new_means.items():
            remapped_clusters[cluster_mapping_dict[key]] = value
        
        return remapped_clusters

    @staticmethod
    def sessions_per_cluster(labels, session_ids, cluster_mapping):
        """
        Groups the session IDs by cluster labels, considering the provided cluster mapping.
        :param labels: Clustering labels (numpy.int64)
        :param session_ids: Clear name of the sessionIDs
        :param cluster_mapping: Mapping of new to previous cluster labels (use None if there is no previous one)
        :return: dict { cluster label -> list of sessions }
        """
        session_dict = defaultdict(list)
        
        for lab, sid in zip(labels, session_ids):
            if cluster_mapping == None:
                session_dict[str(lab)].append(sid)
            else:
                session_dict[cluster_mapping[str(lab)]].append(sid)
        
        return session_dict
