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
        :param X: The sessions as Markov chains
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
