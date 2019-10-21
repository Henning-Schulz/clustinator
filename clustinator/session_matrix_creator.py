'''
@author: Henning Schulz
'''

import time
from datetime import datetime

from elastic_connection import ElasticSessionConnection
from session_matrix import SessionMatrix

class SessionMatrixCreator:
    
    def __init__(self, app_id, tailoring, from_micros, to_micros, collect_session_ids = True):
        self._elastic = ElasticSessionConnection(app_id, tailoring, from_micros, to_micros)
        self.collect_session_ids = collect_session_ids
        
    def create(self):
        """
        Creates and returns the session matrix from the sessions stored in the elasticsearch.
        :return: The created SessionMatrix
        """
        
        print('%s Creating session matrix...' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
        
        endpoints = self._elastic.get_unique_endpoints()
        matrix = SessionMatrix(endpoints, collect_session_ids = self.collect_session_ids)
        
        self._elastic.scroll_for_sessions(matrix.append_sessions)
        
        print('%s Session matrix creation done.' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
        
        return matrix
    
    def update_group_ids(self, sessions_per_cluster):
        """
        Updates the group IDs of the sessions as specified in the passed dict.
        :param sessions_per_cluster: Dict of session IDs per group (cluster) ID.
        """
        
        for beh_id, session_ids in sessions_per_cluster.items():
            self._elastic.set_group_ids(beh_id, session_ids)
