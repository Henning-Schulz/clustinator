'''
@author: Henning Schulz
'''

from elastic_connection import ElasticBehaviorConnection

class BehaviorModel:
    
    def __init__(self, label_encoder, app_id, tailoring, interval_start):
        self.label_encoder = label_encoder
        self._dict_1d = None
        
        self._elastic = ElasticBehaviorConnection(app_id, tailoring, interval_start)
    
    def _load_chain(self, json):
        num_states = len(self.label_encoder.classes_)
        transitions = json['transitions']
        array = [0] * (num_states ** 2)
        
        for from_state in transitions.keys():
            for to_state in transitions[from_state].keys():
                prob = transitions[from_state][to_state]['probability']
                from_idx = self.label_encoder.transform([from_state])[0]
                to_idx = self.label_encoder.transform([to_state])[0]
                array[from_idx * num_states + to_idx] = prob
        
        self._dict_1d[json['id']] = array
    
    def load_json(self):
        """
        Loads the behavior model from the JSON stored in the Elasticsearch.
        """
        
        json = self._elastic.get_latest()
        
        if json is not None:
            self._dict_1d = dict()
            
            for markov_chain in json['markov-chains']:
                self._load_chain(markov_chain)
    
    def as_1d_dict(self):
        """
        Returns the loaded behavior model as a dict of 1d arrays, one per Markov chain.
        The order of the Markov states corresponds to the label encoder.
        The keys are the Markov chain IDs (string).
        """
        
        return self._dict_1d
