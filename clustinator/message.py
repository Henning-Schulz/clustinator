'''
@author: An Dang
'''

import json


class Message:

    def __init__(self, header, cluster_mean, states, think_time_means, think_time_variances, frequency):
        self.header = header
        self.cluster_mean = cluster_mean
        self.states = states
        self.think_time_means = think_time_means
        self.think_time_variances = think_time_variances
        self.frequency = frequency

    def build_json(self):
        """
        Build the json-object
        :return: A jason-dump
        """
        self.header['mean-markov-chains'] = self.cluster_mean
        self.header['states'] = self.states
        self.header['think-time-means'] = self.think_time_means
        self.header['think-time-variances'] = self.think_time_variances
        self.header['frequency'] = self.frequency

        return json.dumps(self.header)
