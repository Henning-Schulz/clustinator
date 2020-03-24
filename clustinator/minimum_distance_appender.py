'''
@author: Henning Schulz
'''

import numpy as np
import time
from datetime import datetime
from sklearn.decomposition import TruncatedSVD

from session_appender import SessionAppender
import math
from random import randrange
from scipy.sparse.base import issparse

class MinimumDistanceAppender(SessionAppender):
    
    cluster_mapping = None
    
    def __init__(self, prev_behavior_models, label_encoder, dimensions=None, radius_factor=None, num_seedings=None, min_samples=None):
        self.dimensions = dimensions
        self.radius_factor = radius_factor if radius_factor else 1.1
        self.min_samples = min_samples if min_samples else 10
        self.num_seedings = num_seedings if num_seedings else 10
        
        # Only using latest behavior model (assumes latest-first ordering)
        if prev_behavior_models:
            self.prev_markov_chains = prev_behavior_models[0].as_1d_dict(label_encoder)
            self.prev_radiuses = prev_behavior_models[0].radiuses(label_encoder)
            self.num_sessions = prev_behavior_models[0].get_num_sessions()
    
    def to_array(self, potential_sparse_array):
        if issparse(potential_sparse_array):
            return potential_sparse_array.toarray()
        else:
            return potential_sparse_array
    
    def _recalculate_mean(self, mid, new_mean, new_num_sessions):
        prev_num_sessions = self.num_sessions.get(mid, 0)
        weighted_prev = [ prev_num_sessions * x for x in self.prev_markov_chains.get(mid, new_mean)]
        weighted_new = [ new_num_sessions * x for x in new_mean ]
        absolute = [ sum(x) for x in zip(weighted_prev, weighted_new) ]
        
        total_num_sessions = prev_num_sessions + new_num_sessions
        self.num_sessions[mid] = total_num_sessions
        
        return [ x / total_num_sessions for x in absolute ]
    
    def _find_cluster(self, reduced_matrix, indices_unassigned, max_radius):
        last_indices = []
        new_indices = [ randrange(len(indices_unassigned)) ]
        centroid = reduced_matrix[indices_unassigned][new_indices]
        
        while last_indices != new_indices:
            last_indices = new_indices
            new_indices = [ idx for idx in indices_unassigned if np.linalg.norm(self.to_array(reduced_matrix[idx] - centroid)) < max_radius ]
            
            centroid = sum(reduced_matrix[new_indices]) / len(new_indices)
        
        return new_indices
    
    def _cluster_remainder(self, reduced_matrix, indices_unassigned, labels, prev_labels):
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Checking whether to group the remaining sessions into a new cluster...')
        
        max_radius = np.amax([r for (mid, r) in self.prev_radiuses.items() if mid != '-1']) * self.radius_factor
        largest_cluster = []
        
        for _ in range(self.num_seedings):
            new_cluster = self._find_cluster(reduced_matrix, indices_unassigned, max_radius)
            
            if len(new_cluster) > len(largest_cluster):
                largest_cluster = new_cluster
        
        if len(largest_cluster) >= self.min_samples:
            new_label = str(max([ int(s) if s.isdigit() else 0 for s in prev_labels ]) + 1)
            labels[largest_cluster] = new_label
            
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Found', len(largest_cluster), 'sessions fitting into one cluster. Assigning them to label', new_label)
        else:
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Did not identify a new cluster.')
            largest_cluster = []
        
        noise_indices = [ idx for idx in indices_unassigned if idx not in largest_cluster ]
        labels[noise_indices] = '-1'
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Clustering of the remaining sessions done.', len(noise_indices), 'sessions have been identified as noise.')
    
    def _assign_sessions(self, csr_matrix, absolute=np.absolute):
        if self.dimensions:
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Reducing the sessions to', self.dimensions, 'dimensions...')
            svd = TruncatedSVD(n_components=self.dimensions)
            reduced_matrix = svd.fit_transform(csr_matrix)
            reduced_means = np.array([ svd.transform([mean_chain])[0] for mean_chain in self.prev_markov_chains.values() ])
        else:
            svd = None
            reduced_matrix = csr_matrix
            reduced_means = np.array([ mean_chain for mean_chain in self.prev_markov_chains.values() ])
        
        label_type = '<U' + str(max(max([ len(x) for x in self.prev_markov_chains.keys() ]), 2))
        unique_labels = np.fromiter(self.prev_markov_chains.keys(), dtype = label_type)
        
        filtered_means = reduced_means[unique_labels != '-1'] # not mapping to noise cluster
        unique_labels = unique_labels[unique_labels != '-1']
        
        num_sessions = csr_matrix.shape[0]
        labels = np.empty(num_sessions, dtype = label_type)
        distances = np.empty(len(filtered_means), dtype='float64')
        indices_unassigned = []
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Classifying the new sessions by minimum distance...')
        
        for i in range(num_sessions):
            row = reduced_matrix[i]
            
            if not svd:
                row = row.toarray()[0]
                
            for j in range(len(filtered_means)):
                diff = row - filtered_means[j]
                dist = np.linalg.norm(diff)
                distances[j] = dist if np.all(diff <= self.radius_factor * absolute(self.prev_radiuses[unique_labels[j]])) else math.inf
            
            min_dist = min(distances)
            
            if min_dist < math.inf:
                labels[i] = unique_labels[np.argmin(distances)]
            else:
                indices_unassigned.append(i)
        
        self._cluster_remainder(reduced_matrix, indices_unassigned, labels, unique_labels)
        
        unique, counts = np.unique(labels, return_counts = True)
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Classification done. Found the following clusters:', unique, 'with counts:', counts)
        
        return unique, counts, labels
    
    def append(self, csr_matrix):
        unique, counts, labels = self._assign_sessions(csr_matrix)
        
        self.labels = labels
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Calculating the cluster means...')
        
        num_sessions = dict(zip(unique, counts))
        new_cluster_means = self._calculate_cluster_means(csr_matrix, self.labels)
        self.cluster_means = { mid: self._recalculate_mean(mid, new_mean, num_sessions[mid]) for mid, new_mean in new_cluster_means.items() }
        
        for (old_mid, old_mean) in self.prev_markov_chains.items():
            if old_mid not in self.cluster_means:
                self.cluster_means[old_mid] = old_mean
                print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Added old cluster mean of group', old_mid, 'as no new session belongs to it.')
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Mean calculation done.')
        
        print("Calculating the cluster radiuses...")
        new_cluster_radiuses = self._calculate_cluster_radiuses(csr_matrix, self.labels, self.cluster_means)
        
        for (old_mid, old_radius) in self.prev_radiuses.items():
            if old_mid not in new_cluster_radiuses:
                new_cluster_radiuses[old_mid] = old_radius
                print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Added old cluster radius of group', old_mid, 'as no new session belongs to it.')
        
        self.cluster_radiuses = { mid: np.maximum(new_radius, self.prev_radiuses.get(mid, new_radius)) for mid, new_radius in new_cluster_radiuses.items() }
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Radius calculation and appending done.')
        
