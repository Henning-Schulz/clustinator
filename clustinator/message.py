import json


class Message:

    def __init__(self, header, cluster_mean, states, session_label):
        self.header = header
        self.cluster_mean = cluster_mean
        self.states = states
        self.session_label = session_label

    def build_json(self):
        """
        Build the json-object
        :return: A jason-dump
        """
        self.header['mean-markov-chains'] = self.cluster_mean
        self.header['states'] = self.states
        self.header['sessions'] = self.session_label

        return json.dumps(self.header)
