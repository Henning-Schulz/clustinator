'''
@author: Henning Schulz
'''

import numpy as np
import time
from datetime import datetime

from session_appender import SessionAppender

class MinimumDistanceAppender(SessionAppender):
    
    cluster_mapping = None
    
    def __init__(self, prev_behavior_models, label_encoder):
        # Only using latest behavior model (assumes latest-first ordering)
        if prev_behavior_models:
            self.prev_markov_chains = prev_behavior_models[0].as_1d_dict(label_encoder)
            self.num_sessions = prev_behavior_models[0].get_num_sessions()
        
    def _classify(self, session):
        distances = []
        mc_ids = []
        
        for mid, mean_chain in self.prev_markov_chains.items():
            dist = np.linalg.norm(session - mean_chain)
            distances.append(dist)
            mc_ids.append(mid)
        
        return mc_ids[np.argmin(distances)]
    
    def _recalculate_mean(self, mid, new_mean, new_num_sessions):
        prev_num_sessions = self.num_sessions[mid]
        weighted_prev = [ prev_num_sessions * x for x in  self.prev_markov_chains[mid]]
        weighted_new = [ new_num_sessions * x for x in new_mean ]
        absolute = [ sum(x) for x in zip(weighted_prev, weighted_new) ]
        
        total_num_sessions = prev_num_sessions + new_num_sessions
        self.num_sessions[mid] = total_num_sessions
        
        return [ x / total_num_sessions for x in absolute ]
    
    def append(self, csr_matrix):
        labels = []
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Classifying the new sessions by minimum distance...')
        
        for row in csr_matrix:
            labels.append(self._classify(row.toarray()[0]))
        
        self.labels = np.array(labels)
        
        unique, counts = np.unique(self.labels, return_counts = True)
        num_sessions = dict(zip(unique, counts))
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Classification done. Found the following clusters:', unique, 'with counts:', counts)
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Calculating the cluster means...')
        
        new_cluster_means = self._calculate_cluster_means(csr_matrix, self.labels)
        
        self.cluster_means = { mid: self._recalculate_mean(mid, new_mean, num_sessions[mid]) for mid, new_mean in new_cluster_means.items() }
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Mean calculation and appending done.')
        
