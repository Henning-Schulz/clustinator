'''
@author: Henning Schulz
'''

from elastic_connection import ElasticBehaviorConnection

class BehaviorModel:
    
    def __init__(self, json):
        self.json = json
    
    def get_endpoints(self):
        """
        Extracts and returns the endpoints contained in this behavior model.
        :return: The endpoints (will NOT contain $ or INITIAL*)
        """
        
        states = set()
        
        if self.json is not None:
            for markov_chain in self.json['markov-chains']:
                for from_state in markov_chain['transitions'].keys():
                    if from_state not in [ '$', 'INITIAL*' ]:
                        states.add(from_state)
        
        return states
    
    def get_num_sessions(self):
        """
        Extract and gets the number of sessions per group.
        :return: A dict { 'markov chain id' -> num_sessions }
        """
        
        num_sessions = dict()
        
        if self.json is not None:
            for markov_chain in self.json['markov-chains']:
                num_sessions[markov_chain['id']] = markov_chain['num-sessions']
        
        return num_sessions
        
    
    def _load_chain(self, json, label_encoder):
        num_states = len(label_encoder.classes_)
        transitions = json['transitions']
        array = [0] * (num_states ** 2)
        
        for from_state in transitions.keys():
            for to_state in transitions[from_state].keys():
                prob = transitions[from_state][to_state]['probability']
                from_idx = label_encoder.transform([from_state])[0]
                to_idx = label_encoder.transform([to_state])[0]
                array[from_idx * num_states + to_idx] = prob
        
        return array
    
    def as_1d_dict(self, label_encoder):
        """
        Returns the loaded behavior model as a dict of 1d arrays, one per Markov chain.
        The order of the Markov states corresponds to the label encoder.
        The keys are the Markov chain IDs (string).
        :param label_encoder: Label encoder to use for getting the index per state.
        :return: A dict { 'markov chain id' -> [1d array (list)] }
        """
        
        if self.json is None:
            return None
        
        dict_1d = dict()
            
        for markov_chain in self.json['markov-chains']:
            array_1d = self._load_chain(markov_chain, label_encoder)
            dict_1d[markov_chain['id']] = array_1d
        
        return dict_1d
    
    def _load_think_time_mean(self, json, label_encoder):
        num_states = len(label_encoder.classes_)
        transitions = json['transitions']
        array = [0] * (num_states ** 2)
        
        for from_state in transitions.keys():
            for to_state in transitions[from_state].keys():
                mean = transitions[from_state][to_state]['thinkTime']['mean']
                from_idx = label_encoder.transform([from_state])[0]
                to_idx = label_encoder.transform([to_state])[0]
                array[from_idx * num_states + to_idx] = mean
        
        return array
    
    def _load_think_time_variance(self, json, label_encoder):
        num_states = len(label_encoder.classes_)
        transitions = json['transitions']
        array = [0] * (num_states ** 2)
        
        for from_state in transitions.keys():
            for to_state in transitions[from_state].keys():
                var = transitions[from_state][to_state]['thinkTime']['variance']
                from_idx = label_encoder.transform([from_state])[0]
                to_idx = label_encoder.transform([to_state])[0]
                array[from_idx * num_states + to_idx] = var
        
        return array
    
    def think_time_means_1d_dict(self, label_encoder):
        """
        Returns the think time means of the loaded behavior model as a dict of 1d arrays, one per Markov chain.
        The order of the Markov states corresponds to the label encoder.
        The keys are the Markov chain IDs (string).
        :param label_encoder: Label encoder to use for getting the index per state.
        :return: A dict { 'markov chain id' -> [1d array (list)] }
        """
        
        if self.json is None:
            return None
        
        dict_1d = dict()
            
        for markov_chain in self.json['markov-chains']:
            array_1d = self._load_think_time_mean(markov_chain, label_encoder)
            dict_1d[markov_chain['id']] = array_1d
        
        return dict_1d
    
    def think_time_variances_1d_dict(self, label_encoder):
        """
        Returns the think time variances of the loaded behavior model as a dict of 1d arrays, one per Markov chain.
        The order of the Markov states corresponds to the label encoder.
        The keys are the Markov chain IDs (string).
        :param label_encoder: Label encoder to use for getting the index per state.
        :return: A dict { 'markov chain id' -> [1d array (list)] }
        """
        
        if self.json is None:
            return None
        
        dict_1d = dict()
            
        for markov_chain in self.json['markov-chains']:
            array_1d = self._load_think_time_variance(markov_chain, label_encoder)
            dict_1d[markov_chain['id']] = array_1d
        
        return dict_1d
