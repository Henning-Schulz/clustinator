'''
@author: Henning Schulz
'''

from sklearn.cluster import DBSCAN
import numpy as np
import time
from datetime import datetime

from session_appender import SessionAppender
from analysis.cluster_analysis import Cluster_analysis as ca

class DbscanAppender(SessionAppender):
    
    def __init__(self, epsilon, avg_tolerance, n_states, min_samples, prev_behavior_models, label_encoder):
        if epsilon is None and avg_tolerance is not None:
            epsilon = (len(n_states) - 1) * avg_tolerance
        
        self.epsilon = epsilon
        self.min_samples = min_samples
        self.prev_behavior_models = prev_behavior_models
        self.label_encoder = label_encoder
    
    def _do_clustering(self, csr_matrix):
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Starting the clustering with epsilon', self.epsilon, '...')
        labels = DBSCAN(eps=self.epsilon, min_samples=self.min_samples).fit(csr_matrix).labels_
        unique, counts = np.unique(labels, return_counts=True)
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Clustering done. Found the following clusters:', unique, 'with counts:', counts)
        
        return unique, counts, labels
        
    def _remap_clusters(self, cluster_means, counts):
        if not self.prev_behavior_models:
            cluster_mapping = None
        else:
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Mapping to the previous Markov chains...')
            cluster_analysis = ca(self.prev_behavior_models, cluster_means, counts, self.label_encoder)
            cluster_mapping = cluster_analysis.cluster_mapping(self.epsilon)
            cluster_means = cluster_analysis.relabel_clusters(cluster_mapping)
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Calculated mapping:', cluster_mapping)
        
        return cluster_means, cluster_mapping
    
    def append(self, csr_matrix):
        unique, counts, labels = self._do_clustering(csr_matrix)
        
        print("Calculating the cluster means...")
        cluster_means = self._calculate_cluster_means(csr_matrix, labels)
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Mean calculation done. Calculating the cluster means and mapping...')
        
        cluster_means, cluster_mapping = self._remap_clusters(cluster_means, counts)
        
        self.cluster_means = cluster_means
        self.labels = labels
        self.cluster_mapping = cluster_mapping
        
        print("Calculating the cluster radiuses...")
        self.cluster_radiuses = self._calculate_cluster_radiuses(csr_matrix, labels, cluster_means)
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Radius calculation done.')
        
        self.num_sessions = { cluster_mapping[str(mid)] : count for mid, count in zip(unique, counts) }
