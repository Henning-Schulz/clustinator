'''
@author: An Dang, Henning Schulz
'''

import json
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


class Message:

    def __init__(self, header, cluster_mean, states, think_time_means, think_time_variances, frequency, num_sessions):
        self.header = header
        self.cluster_mean = cluster_mean
        self.states = states
        self.think_time_means = think_time_means
        self.think_time_variances = think_time_variances
        self.frequency = frequency
        self.num_sessions = num_sessions

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
        self.header['num-sessions'] = self.num_sessions

        return json.dumps(self.header, cls=NpEncoder)
