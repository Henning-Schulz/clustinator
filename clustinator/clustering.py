from sklearn.cluster import DBSCAN
import numpy as np


states = ["INITIAL","login","View_Items","home","logout","View_Items_quantity","Add_to_Cart","shoppingcart",
          "remove","deferorder","purchasecart","inventory","sellinventory","clearcart","cancelorder","$"]

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

    def dbscan(self):
        return DBSCAN(eps=self.eps, min_samples=self.min_samples).fit(self.X)

    def unique_labels(self):
        labels = self.dbscan().labels_
        unique, counts = np.unique(labels, return_counts=True)
        return unique, counts, labels

    def compare_results(self):
        unique, counts = self.unique_labels()
        # represent the cluster results as dict
        result = dict(zip(unique, counts))

        return result

    # Dict_Cluster
    @staticmethod
    def cluster_dict(labels, X_):
        cluster_list = []

        for label in np.unique(labels):
            points = X_[labels == label].toarray()

            for point in points:
                cluster_dict = {}
                cluster_dict[label] = point
                cluster_list.append(cluster_dict)

        return cluster_list

    @staticmethod
    def list_cluster(cluster_dict_, labels_next, labels_past):
        """
        TODO: Check if the clusterlabels are equal, it's because an error can be accurse at the analysis
        :param cluster_dict_: dict of all cluster with clusterlabels e.g. [0,1,2,...]
        :param labels_next: actuall labels
        :param labels_past: older labels
        :return: list of cluster mean markov-chains
        """
        cluster_list = []
        result = {}

        # Initial list cluster
        if labels_past is None:
            for cluster_index, value in enumerate(np.unique(labels_next)):
                tmp = []
                for item in cluster_dict_:
                    for k, v in item.items():
                        if k == value:
                            tmp.append(v.tolist())
                cluster_list.append(np.mean(tmp, axis=0))

            for index, value in enumerate(cluster_list):
                for value1 in np.unique(labels_next):
                    result[str(value1)] = value

            return result

        # From the second pass on
        elif np.unique(labels_next) in labels_past:
            for cluster_index, value in enumerate(np.unique(labels_next)):
                tmp = []
                for item in cluster_dict_:
                    for k, v in item.items():
                        if k == value:
                            tmp.append(v.tolist())
                cluster_list.append(np.mean(tmp, axis=0))
            return cluster_list

        else:
            print('Unequally Number of cluster labels. Actual cluster {actualcluster} old cluster {oldcluster}'.format(
                actualcluster=np.unique(labels_next), oldcluster=labels_past))
            for cluster_index, value in enumerate(np.unique(labels_next)):
                tmp = []
                for item in cluster_dict_:
                    for k, v in item.items():
                        if k == value:
                            tmp.append(v.tolist())
                cluster_list.append(np.mean(tmp, axis=0))
            return cluster_list