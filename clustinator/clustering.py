'''
@author: An Dang, Henning Schulz
'''

from sklearn.cluster import DBSCAN
import numpy as np
import math

# Data imports
PATH = "../data/raw/"
sessions_file = (PATH+'sessions.dat')


class Clustering:
    
    def __init__(self, X, eps, min_samples):
        """
        Class for the DBSCAN clustering algorithm with sklearn.
        :param X: Input data for the clustering
        """
        self.X = X
        self.eps = eps
        self.min_samples = min_samples

        self.dbscan = DBSCAN(eps=self.eps, min_samples=self.min_samples).fit(self.X)

    def label_summary(self):
        """
        Returns a summary of the cluster labels.
        :return: unique cluster labels, points per cluster, all labels (array)
        """
        
        labels = self.dbscan.labels_
        unique, counts = np.unique(labels, return_counts=True)
        return unique, counts, labels
    
    def cluster_means(self):
        """
        Returns the clustering results as dict of mean markov chain per cluster label.
        :return: { cluster label (str) -> mean markov chain }
        """
        
        labels = self.dbscan.labels_
        cluster_mean_dict = {}
        
        for label in np.unique(labels):
            chains_with_label = self.X[labels == label]
            mean_chain = sum(chains_with_label) / chains_with_label.shape[0]
            mean_chain = mean_chain.toarray()[0].tolist()
            row_length = int(round(math.sqrt(len(mean_chain))))
            
            for i in range(len(mean_chain) // row_length):
                row_sum = sum(mean_chain[i * row_length:(i+1) * row_length])
                
                if row_sum > 0 and abs(row_sum - 1.0) > 0.001:
                    # if a session misses an endpoint, that row will be 0 --> mean can be less than 1
                    for j in range(i * row_length, (i+1) * row_length):
                        mean_chain[j] = mean_chain[j] / row_sum
            
            cluster_mean_dict[str(label)] = mean_chain
        
        return cluster_mean_dict
