'''
@author: Henning Schulz
'''

import numpy as np
import time
from datetime import datetime
from sklearn.decomposition import TruncatedSVD

from session_appender import SessionAppender

class MinimumDistanceAppender(SessionAppender):
    
    cluster_mapping = None
    
    def __init__(self, prev_behavior_models, label_encoder, dimensions=None):
        self.dimensions = dimensions
        
        # Only using latest behavior model (assumes latest-first ordering)
        if prev_behavior_models:
            self.prev_markov_chains = prev_behavior_models[0].as_1d_dict(label_encoder)
            self.num_sessions = prev_behavior_models[0].get_num_sessions()
    
    def _recalculate_mean(self, mid, new_mean, new_num_sessions):
        prev_num_sessions = self.num_sessions[mid]
        weighted_prev = [ prev_num_sessions * x for x in  self.prev_markov_chains[mid]]
        weighted_new = [ new_num_sessions * x for x in new_mean ]
        absolute = [ sum(x) for x in zip(weighted_prev, weighted_new) ]
        
        total_num_sessions = prev_num_sessions + new_num_sessions
        self.num_sessions[mid] = total_num_sessions
        
        return [ x / total_num_sessions for x in absolute ]
    
    def append(self, csr_matrix):
        if self.dimensions:
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Reducing the sessions to', self.dimensions, 'dimensions...')
            svd = TruncatedSVD(n_components=self.dimensions)
            reduced_matrix = svd.fit_transform(csr_matrix)
            reduced_means = [ svd.transform([mean_chain])[0] for mean_chain in self.prev_markov_chains.values() ]
        else:
            svd = None
            reduced_matrix = csr_matrix
            reduced_means = [ mean_chain for mean_chain in self.prev_markov_chains.values() ]
        
        label_type = '<U' + str(max([ len(x) for x in self.prev_markov_chains.keys() ]))
        unique_labels = np.fromiter(self.prev_markov_chains.keys(), dtype = label_type)
        num_sessions = csr_matrix.shape[0]
        self.labels = np.empty(num_sessions, dtype = label_type)
        distances = np.empty(len(reduced_means), dtype='float64')
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Classifying the new sessions by minimum distance...')
        
        for i in range(num_sessions):
            row = reduced_matrix[i]
            
            if not svd:
                row = row.toarray()[0]
                
            for j in range(len(reduced_means)):
                distances[j] = np.linalg.norm(row - reduced_means[j])
            
            self.labels[i] = unique_labels[np.argmin(distances)]
        
        unique, counts = np.unique(self.labels, return_counts = True)
        num_sessions = dict(zip(unique, counts))
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Classification done. Found the following clusters:', unique, 'with counts:', counts)
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Calculating the cluster means...')
        
        new_cluster_means = self._calculate_cluster_means(csr_matrix, self.labels)
        
        self.cluster_means = { mid: self._recalculate_mean(mid, new_mean, num_sessions[mid]) for mid, new_mean in new_cluster_means.items() }
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Mean calculation and appending done.')
        
