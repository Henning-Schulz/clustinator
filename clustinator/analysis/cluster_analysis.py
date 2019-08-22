import numpy as np

old_min_points = {}
cluster_mean_history = {}
min_point_label_list = []

class Cluster_analysis:

    def __init__(self, first_dict, second_list):
        self.first_dict = first_dict
        self.second_list = second_list

    def cluster_backprob(self):
        """
        TODO: BUG: https://continuity-project.atlassian.net/browse/CONT-255
        In this function we backpropagate the clustering and compare the results from the two clustering results.
        If there is shifting of the clusters, the clusters will be re labeled
        :return: A dictionary with the clusterlabls and the mean-markov-chain.
        Also a list with the shifting clusterlabels.
        """

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

            min_point_label_list.append(min_point_dict[min(sum_mean_vector_list)])

            # Labeling the new cluster points to the shifting cluster (only key)
            cluster_mean_history[str(min_point_dict[min(sum_mean_vector_list)][0])] = second_list_dict[
                value_subtraction_sum_dict[min(sum_mean_vector_list)][1]
            ]

            # No. of cluster with corresponding clusterpoints (add value)
            tmp = second_list_dict[min_point_dict[min(sum_mean_vector_list)][1]]

            # The real matching of labeling the shifting cluster
            cluster_mean_history[str(index)] = tmp

        return cluster_mean_history, min_point_label_list

    @staticmethod
    def get_session_label(labels, session_id, min_point_label_list):
        """
        In this function clusterlabels and sessionids are zip together.
        :param labels: Clustering labels
        :param session_id: Clear name of the sessionIDs
        :param min_point_label_list: Update the Clustering label if it's shifted
        :return: A dict with Clusterlabels and a list with it's sessionIDs
        """
        label_zip = list(zip(labels, session_id))
        tmp_dict = dict()
        [tmp_dict[t[0]].append(t[1]) if t[0] in list(tmp_dict.keys())
         else dict.update({t[0]: [t[1]]}) for t in label_zip]
        new_dict = dict([(str(k), v) for k, v in tmp_dict.items()])

        if min_point_label_list != None:
            for key_pair in min_point_label_list:
                new_dict[str(key_pair[0])] = new_dict.pop(str(key_pair[1]))
            return new_dict
        else:
            return new_dict

