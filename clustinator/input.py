'''
@author: An Dang, Henning Schulz
'''

import json


class Input:

    def __init__(self, sessions_json):
        self.data = json.loads(sessions_json)

    def dbscan_param(self):
        return self.data.get('avg-transition-tolerance'), self.data.get('epsilon'), self.data.get('min-sample-size')
    
    def kmeans_param(self):
        return self.data.get('k'), self.data.get('max-iterations'), self.data.get('num-seedings'), self.data.get('convergence-tolerance'), self.data.get('parallelize')

    def get_header(self):
        header_dict = {}
        header_list = ['app-id', 'version', 'tailoring', 'append-strategy',
                       'start-micros', 'interval-start-micros', 'end-micros', 'continuation']
        for header in header_list:
            for k, v in self.data.items():
                if k == header:
                    header_dict[k] = v
        
        return header_dict

    def get_prev_markov_chain(self):
        return self.data['previous-markov-chains']

    def get_app_id(self):
        return self.data['app-id']
    
    def get_tailoring(self):
        return self.data['tailoring']
    
    def get_range_micros(self):
        return self.data['start-micros'], self.data['interval-start-micros'], self.data['end-micros']
    
    def get_lookback(self):
        return self.data['lookback']
    
    def get_append_strategy(self):
        return self.data.get('append-strategy')
    
    def get_dimensions(self):
        return self.data.get('dimensions')
    
