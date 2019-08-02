from sklearn.cluster import DBSCAN
import numpy as np


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

    def list_cluster(self, cluster_dict_):
        cluster_list = []
        if labels_1 in labels_2:
            for cluster_index, value in enumerate(np.unique(labels_1)):
                tmp = []
                for item in cluster_dict_:
                    for k, v in item.items():
                        if k == cluster_index:
                            tmp.append(v.tolist())
                # print(tmp)
                cluster_list.append(np.mean(tmp, axis=0))

        return cluster_list
