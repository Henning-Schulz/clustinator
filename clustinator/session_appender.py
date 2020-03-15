'''
@author: Henning Schulz
'''

import numpy as np
import abc

class SessionAppender:
    """
    Abstract class for appending new sessions to the (non) existing behavior models.
    
    Attributes:
        cluster_means: The cluster means { new cluster label (str) -> mean markov chain }. Available after a call to append(csr_matrix).
        labels: The labels of the sessions in the order of the specified csr matrix. Available after a call to append(csr_matrix).
        cluster_mapping: Mapping of new labels to old labels { new cluster label -> previous cluster label } or None (means identity). Available after a call to append(csr_matrix).
        num_sessions: The number of sessions per cluster { new cluster label -> number of sessions }. Available after a call to append(csr_matrix).
    """
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def append(self, csr_matrix):
        """
        Appends the Markov chains to the previous ones.
        :param csr_matrix: The Markov chains (CSR matrix format)
        """
        return
    
    def _calculate_cluster_means(self, X, labels):
        """
        Returns the cluster means as dict of mean markov chain per group label.
        :param X: The sessions as (absolute) Markov chains
        :param labels: The labels per Markov chain in the same order as X
        :return: { group label (str) -> mean markov chain }
        """
        
        cluster_mean_dict = {}
        
        for label in np.unique(labels):
            chains_with_label = X[labels == label]
            mean_chain = sum(chains_with_label) / chains_with_label.shape[0]
            mean_chain = mean_chain.toarray()[0].tolist()
            
            cluster_mean_dict[str(label)] = mean_chain
        
        return cluster_mean_dict
    
    def _calculate_cluster_radiuses(self, X, labels, cluster_means):
        """
        Returns the radius of each cluster (maximum distance of a session to the cluster mean).
        :param X: The sessions as (absolute) Markov chains
        :param labels: The labels per Markov chain in the same order as X
        :param cluster_means: The cluster means as returned by _calculate_cluster_means(X, labels).
        :return: { group label (str) -> cluster radius }
        """
        
        cluster_radius_dict = {}
        
        for label in np.unique(labels):
            chains_with_label = X[labels == label]
            mean_chain = cluster_means[str(label)]
            
            cluster_radius_dict[str(label)] = max([ np.linalg.norm(chains_with_label[i].toarray() - mean_chain) for i in range(chains_with_label.shape[0]) ])
        
        return cluster_radius_dict
