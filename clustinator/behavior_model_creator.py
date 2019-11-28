'''
@author: Henning Schulz
'''

from elastic_connection import ElasticBehaviorConnection
from behavior_model import BehaviorModel

class BehaviorModelCreator:
    
    def __init__(self, app_id, tailoring, interval_start):
        self.elastic = ElasticBehaviorConnection(app_id, tailoring, interval_start)
    
    def load(self, n):
        """
        Load the last n behavior models.
        :param n: The numer of behavior models to be loaded.
        :return: List of BehaviorModel.
        """
        
        json_list = self.elastic.get_latest(n)
        
        return [ BehaviorModel(json) for json in json_list ]
