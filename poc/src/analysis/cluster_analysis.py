import numpy as np
from clustering import Clustering
"""# Dict_Cluster
def cluster_dict(labels, X_):
    cluster_list = []

    for label in np.unique(labels):
        points = X_[labels == label].toarray()

        for point in points:
            cluster_dict = {}
            cluster_dict[label] = point
            cluster_list.append(cluster_dict)

    return cluster_list"""

"""def list_cluster(cluster_dict_):
    cluster_list = []
    if labels_1 in labels_2:
        for cluster_index, value in enumerate(np.unique(labels_1)):
            tmp = []
            for item in cluster_dict_:
                for k,v in item.items():
                    if k == cluster_index:
                        tmp.append(v.tolist())
            #print(tmp)
            cluster_list.append(np.mean(tmp, axis=0))
    return cluster_list"""


old_min_points = {}
cluster_mean_history = {}

class Cluster_analysis:

    def __init__(self, cluster_dict_next, cluster_dict_past):
        self.cluster_dict_next = cluster_dict_next
        self.cluster_dict_past = cluster_dict_past

    def cluster_backprob(self):
        first_list = Clustering.list_cluster(self.cluster_dict_next)
        second_list = Clustering.list_cluster(self.cluster_dict_past)

        #mylist = [first_list, second_list]
        for index, value in enumerate(first_list):
            min_point_dict = {}
            value_subtraction_sum_dict = {}
            second_list_dict = {}
            sum_mean_vector_list = []

            for second_index, second_value in enumerate(second_list):
                # Indexing dict from second_list
                second_list_dict[second_index] = second_value
                # Min vector subtraction with first and second index
                min_point_dict[sum(abs(np.array(value) - np.array(second_value)))] = [index, second_index]
                # Sum of the subtraction and the abs vector subtraction (for matching)
                value_subtraction_sum_dict[sum(abs(np.array(value) - np.array(second_value)))] = abs(
                    np.array(value) - np.array(second_value))
                # sum mean vector as list for matching
                sum_mean_vector_list.append(sum(abs(np.array(value) - np.array(second_value))))

            # Normal labled clusterpoints bevore compute the shifting
            old_min_points[min_point_dict[min(sum_mean_vector_list)][0]] = second_list_dict[
                value_subtraction_sum_dict[min(sum_mean_vector_list)][1]
            ]

            # Labeling the new cluster points to the shifting cluster
            cluster_mean_history[min_point_dict[min(sum_mean_vector_list)][0]] = second_list_dict[
                value_subtraction_sum_dict[min(sum_mean_vector_list)][1]
            ]

            # No. of cluster with corresponding clusterpoints
            tmp = [second_list_dict[min_point_dict[min(sum_mean_vector_list)][1]]]
            tmp.append(value)

            cluster_mean_history[index] = tmp

            # print(min_point_dict[min(sum_mean_vector_list)])
            print(cluster_mean_history)

        return cluster_mean_history


