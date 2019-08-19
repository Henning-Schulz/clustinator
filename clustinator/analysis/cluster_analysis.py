import numpy as np

old_min_points = {}
cluster_mean_history = {}


class Cluster_analysis:

    def __init__(self, first_dict, second_list):
        self.first_dict = first_dict
        self.second_list = second_list

    def cluster_backprob(self):

        for index, value in self.first_dict.items():
            min_point_dict = {}
            value_subtraction_sum_dict = {}
            second_list_dict = {}
            sum_mean_vector_list = []

            for second_index, second_value in enumerate(self.second_list):
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
            cluster_mean_history[str(min_point_dict[min(sum_mean_vector_list)][0])] = second_list_dict[
                value_subtraction_sum_dict[min(sum_mean_vector_list)][1]
            ]

            # No. of cluster with corresponding clusterpoints
            tmp = second_list_dict[min_point_dict[min(sum_mean_vector_list)][1]]
            cluster_mean_history[str(index)] = tmp

        return cluster_mean_history


