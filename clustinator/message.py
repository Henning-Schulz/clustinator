import json


class Message:

    def __init__(self, header, cluster_mean, states):
        self.header = header
        self.cluster_mean = cluster_mean
        self.states = states

    def build_json(self):
        self.header['mean-markov-chains'] = self.cluster_mean
        self.header['states'] = self.states

        return json.dumps(self.header)
