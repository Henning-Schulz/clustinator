'''
@author: Henning Schulz
'''

from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors
import numpy as np
import time
from datetime import datetime
from _warnings import warn

from session_appender import SessionAppender

class KmeansAppender(SessionAppender):
    
    def __init__(self, prev_behavior_models, k, max_iterations = None, num_seedings = None, tolerance = None, n_jobs=1, dimensions=None, quantile_range = None):
        self.k = k
        self.n_jobs = n_jobs
        self.dimensions = dimensions
        self.max_iterations = max_iterations if max_iterations else 300
        self.num_seedings = num_seedings if num_seedings else 10
        self.tolerance = tolerance if tolerance else 1e-4
        self.quantile_range = quantile_range if quantile_range else 0.9
        
        if prev_behavior_models:
            self._do_remap = True
        else:
            self._do_remap = False
    
    def _do_clustering(self, csr_matrix):
        if self.dimensions:
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Reducing the sessions to', self.dimensions, 'dimensions...')
            reduced_matrix = TruncatedSVD(n_components=self.dimensions).fit_transform(csr_matrix)
        else:
            reduced_matrix = csr_matrix
        
        labels = np.full(csr_matrix.shape[0], -1)
        indices = np.arange(csr_matrix.shape[0])
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Checking for outliers with quantile range', self.quantile_range, '...')
        
        neigh = NearestNeighbors(n_neighbors=2)
        neigh.fit(reduced_matrix)
        distances, _ = neigh.kneighbors(reduced_matrix)
        q_lower, q_higher = np.quantile(distances[:,1], [0.5 - self.quantile_range/2, 0.5 + self.quantile_range/2])
        
        non_outlier = distances[:,1] <= q_higher + 1.5 * (q_higher - q_lower)
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Removing', csr_matrix.shape[0] - np.count_nonzero(non_outlier),
              'outliers based on q[', 0.5 - self.quantile_range/2, '] =', q_lower, 'and q[', 0.5 + self.quantile_range/2, '] =', q_higher)
        
        reduced_matrix = reduced_matrix[non_outlier]
        indices = indices[non_outlier]
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Starting the clustering with k =', self.k, ' max_iter =', self.max_iterations,
              ' n_init =', self.num_seedings, ' tol =', self.tolerance, ' n_jobs =', self.n_jobs, '...')
        kmeans = KMeans(n_clusters=self.k, max_iter=self.max_iterations, n_init=self.num_seedings, tol=self.tolerance, n_jobs=self.n_jobs, init='k-means++').fit(reduced_matrix)
        np.put(labels, indices, kmeans.labels_)
        
        if kmeans.n_iter_ >= self.max_iterations:
            warn('The number of iterations reached the specified maximum. The centroids might not have converged!')
        
        unique, counts = np.unique(labels, return_counts=True)
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Clustering done. Needed', kmeans.n_iter_, 'iterations and found the following clusters:', unique, 'with counts:', counts)
        
        return unique, counts, labels
    
    def append(self, csr_matrix):
        unique, counts, labels = self._do_clustering(csr_matrix)
        
        print("Calculating the cluster means...")
        cluster_means = self._calculate_cluster_means(csr_matrix, labels)
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Mean calculation done.')
        
        if self._do_remap:
            warn('Remapping the clusters to previous ones is not implemented yet! Use the minimum-distance strategy instead.')
        
        self.cluster_means = cluster_means
        self.labels = labels
        self.cluster_mapping = None
        
        print("Calculating the cluster radiuses...")
        self.cluster_radiuses = self._calculate_cluster_radiuses(csr_matrix, labels, cluster_means)
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Radius calculation done. Found the following:', self.cluster_radiuses)
        
        self.num_sessions = { str(mid) : count for mid, count in zip(unique, counts) }
