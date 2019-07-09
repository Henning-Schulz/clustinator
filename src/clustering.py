from sklearn.cluster import DBSCAN
import numpy as np
import datetime
import time

from input import Input
from markovchain import MarkovChain


states = ["INITIAL","login","View_Items","home","logout","View_Items_quantity","Add_to_Cart","shoppingcart",
          "remove","deferorder","purchasecart","inventory","sellinventory","clearcart","cancelorder","$"]

# Data imports
PATH = "../data/raw/"
sessions_file = (PATH+'sessions.dat')


class Clustering:
    def __init__(self, X):
        """
        Class for the DBSCAN clustering algorithm with sklearn.
        :param X: Input data for the clustering
        """
        self.X = X

    def dbscan(self):

        return DBSCAN(eps=1.5, min_samples=10).fit(self.X)

    def unique_labels(self):
        labels = self.dbscan().labels_
        unique, counts = np.unique(labels, return_counts=True)
        return unique, counts

    def compare_results(self):
        unique, counts = self.unique_labels()
        # represent the cluster results as dict
        result = dict(zip(unique, counts))

        return result
