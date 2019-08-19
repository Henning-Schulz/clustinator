import json
import pandas as pd


class Input:

    def __init__(self, sessions_file):
        self.sessions_file = sessions_file

    def sessions(self):
        """
        In this function the raw session data is load in. Beside from the whole session data can be slice out dataframe.
        :param slice_from: start slice from - int
        :param slice_to: end slice to - int
        :return: The whole dataframe or sliced dataframe and the states.
        """
        data = json.loads(self.sessions_file)
        s_r_dict = {}

        for sessions in data['sessions']:
            tmp_list = []
            key = sessions['unique-id']
            for value in sessions['requests']:
                tmp_list.append(value['endpoint'])
            s_r_dict[key] = tmp_list

        states = data['states']

        return s_r_dict, states

    def cluster_param(self):
        data = json.loads(self.sessions_file)
        cluster_param = ['epsilon', 'min-sample-size']
        params = []
        for param in cluster_param:
            params.append(data[param])
        epsilon = params[0]
        min_samples = params[1]
        return epsilon, min_samples

    def get_header(self):
        data = json.loads(self.sessions_file)
        header_dict = {}
        header_list = ['app-id', 'version', 'tailoring', 'start-micros',
                       'interval-start-micros', 'end-micros']
        for header in header_list:
            for k, v in data.items():
                if k == header:
                    header_dict[k] = v
        return header_dict

    def get_prev_markov_chain(self):
        data = json.loads(self.sessions_file)
        return data['previous-markov-chains']

    def get_app_id(self):
        data = json.loads(self.sessions_file)
        return data['app-id']
