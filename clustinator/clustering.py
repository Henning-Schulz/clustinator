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
    def cluster_dict(self, labels, X_):
        cluster_list = []

        for label in np.unique(labels):
            points = X_[labels == label].toarray()

            for point in points:
                cluster_dict = {}
                cluster_dict[label] = point
                cluster_list.append(cluster_dict)

        return cluster_list

    def list_cluster(self, cluster_dict_, labels_next, labels_past):
        """
        TODO: was machen bei ungleich?
        :param cluster_dict_: dict of all cluster with labels
        :param labels_next: actuall labels
        :param labels_past: older labels
        :return: list of cluster mean markov-chains
        """
        cluster_list = []
        if np.unique(labels_next) in labels_past:
            for cluster_index, value in enumerate(np.unique(labels_next)):
                tmp = []
                for item in cluster_dict_:
                    for k, v in item.items():
                        if k == cluster_index:
                            tmp.append(v.tolist())
                cluster_list.append(np.mean(tmp, axis=0))
        else:
            print('Unequally Number of cluster labels. Actual cluster {actualcluster} old cluster {oldcluster}'.format(
                actualcluster=np.unique(labels_next), oldcluster=labels_past))
            for cluster_index, value in enumerate(np.unique(labels_next)):
                tmp = []
                for item in cluster_dict_:
                    for k, v in item.items():
                        if k == cluster_index:
                            tmp.append(v.tolist())
                cluster_list.append(np.mean(tmp, axis=0))

        return cluster_list

    def first_cluster(self, cluster_dict_, labels_next):
        result = {}
        cluster_list = []

        for cluster_index, value in enumerate(np.unique(labels_next)):
            print(cluster_index, value)
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
