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
        
    def create(self, extra_endpoints = None):
        """
        Creates and returns the session matrix from the sessions stored in the elasticsearch.
        :return: The created SessionMatrix
        """
        
        print('%s Creating session matrix...' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
        
        endpoints = self._elastic.get_unique_endpoints()
        
        if extra_endpoints is not None:
            endpoints = list(set(endpoints + extra_endpoints))
        
        matrix = SessionMatrix(endpoints, collect_session_ids = self.collect_session_ids)
        
        self._elastic.scroll_for_sessions(matrix.append_sessions)
        
        print('%s Session matrix creation done.' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
        
        return matrix
    
    def update_group_ids(self, sessions_per_cluster, chunk_size = 2000):
        """
        Updates the group IDs of the sessions as specified in the passed dict.
        :param sessions_per_cluster: Dict of session IDs per group (cluster) ID.
        :param chunk_size: The number of sessions to update with one request. Defaults to 2000.
        """
        
        for beh_id, session_ids in sessions_per_cluster.items():
            
            for chunk in [
                session_ids[i * chunk_size:(i + 1) * chunk_size]
                for i in range((len(session_ids) + chunk_size - 1) // chunk_size )
                ]:
                
                self._elastic.set_group_ids(beh_id, chunk)
