'''
@author: An Dang, Henning Schulz
'''

import numpy as np
from collections import defaultdict
from sklearn.neighbors import KNeighborsClassifier

from behavior_model import BehaviorModel

class Cluster_analysis:

    def __init__(self, prev_behavior_models, new_means, cluster_counts, label_encoder):
        self.new_means = new_means
        self.cluster_counts = cluster_counts
        
        self.n_neighbors = len(prev_behavior_models)
        
        prev_means = []
        prev_labels = []
        
        for bm in prev_behavior_models:
            for group, chain in bm.as_1d_dict(label_encoder).items():
                prev_labels.append(group)
                prev_means.append(np.array(chain))
        
        self.prev_means = np.array(prev_means)
        self.prev_labels = np.array(prev_labels)
    
    def _check_int(self, s):
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()
    
    def _mean_comparison(self, new_mean, prev_means, epsilon):
        mean_mean = sum(prev_means) / len(prev_means)
        max_dist = float('inf') if len(prev_means) == 1 else max([ np.linalg.norm(m - mean_mean) for m in prev_means ]) + epsilon
        new_dist = np.linalg.norm(new_mean - mean_mean)
        
        return new_dist, max_dist
    
    def cluster_mapping(self, epsilon):
        """
        Calculates the mapping of cluster labels in the new clustering to labels in the previous clustering.
        Please note that several new labels might be mapped to the same previous label.
        :param epsilon: The epsilon range to look around the cluster means plus max distance
        :return: dict { new cluster label -> previous cluster label }
        """
        
        mapping = {}
        unmapped = []
        
        # do knn classification
        
        new_mean_chains = np.array(list(self.new_means.values()))
        new_labels = np.array(list(self.new_means.keys()))
        
        neigh = KNeighborsClassifier(n_neighbors=self.n_neighbors)
        neigh.fit(self.prev_means, self.prev_labels)
        classification = neigh.predict(new_mean_chains)
        
        # calculate distance to mean of previous means
        
        for i in range(len(new_mean_chains)):
            prev_label = classification[i]
            new_label = new_labels[i]
            
            means_with_label = self.prev_means[self.prev_labels == prev_label]
            dist_to_mean, max_distance = self._mean_comparison(new_mean_chains[i], means_with_label, epsilon)
            
            if dist_to_mean <= max_distance:
                print('  mapping (new %r -> prev %r): diff %r (max %r)' % (new_label, prev_label, dist_to_mean, max_distance))
                mapping[new_label] = (prev_label, dist_to_mean, len(means_with_label))
            else:
                print('  NOT mapping (new %r -> prev %r): diff %r (max %r)' % (new_label, prev_label, dist_to_mean, max_distance))
                unmapped.append(new_label)
        
        # don't merge the first time
        
        new_per_prev = defaultdict(list)
        
        for new_lab, (prev_lab, dist, l) in mapping.items():
            if l == 1:
                new_per_prev[prev_lab].append((new_lab, dist))
        
        for vals in new_per_prev.values():
            if len(vals) > 1:
                dists = [ dist for (_, dist) in vals ]
                del vals[dists.index(min(dists))]
                remapped = [ lab for (lab, _) in vals ]
                
                print('  re-mapping new %r because of first mapping' % remapped)
                unmapped.extend(remapped)
                
        mapping = { new_lab : prev_lab for (new_lab, (prev_lab, _, _)) in mapping.items() }
        
        # append unmapped with fresh numbers
        
        int_labels = [ int(x) for x in self.prev_labels if self._check_int(x) ]
        
        for label in unmapped:
            new_label = int(label)
            
            while new_label in int_labels:
                new_label += (1 if new_label >= 0 else -1)
            
            print('  mapping (new %r -> new %r)' % (label, new_label))
            mapping[label] = str(new_label)
        
        return mapping
    
    def _merge_means(self, mean_chains, label):
        if len(mean_chains) == 1:
            return mean_chains[0][0]
        else:
            print('  merging %d cluster means to prev label %r' % (len(mean_chains), label))
            return (sum([ count * np.array(chain) for (chain, count) in mean_chains ]) / sum([ count for (_, count) in mean_chains ])).tolist()
    
    def relabel_clusters(self, cluster_mapping_dict):
        """
        Relabels the clusters based on the provided mapping.
        :param cluster_mapping_dict: The mapping of new to previous cluster labels
        :return: dict { previous cluster label -> mean markov chain } 
        """
        
        remapped_clusters = defaultdict(list)
        index_offset = 1 if '-1' in self.new_means else 0
        
        for key, value in self.new_means.items():
            count = self.cluster_counts[int(key) - index_offset]
            remapped_clusters[cluster_mapping_dict[key]].append((value, count))
        
        return { key : self._merge_means(value, key) for (key, value) in remapped_clusters.items() }

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
