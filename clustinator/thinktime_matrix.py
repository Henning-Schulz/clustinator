'''
@author: Henning Schulz
'''

import time
from datetime import datetime
import array
import numpy as np

from elastic_connection import ElasticSessionConnection

class ThinktimeMatrix:
    
    def __init__(self, app_id, tailoring, from_micros, to_micros, label_encoder):
        self.label_encoder = label_encoder
        
        self._num_states = len(label_encoder.classes_)
        self._thinktimes = {}
        
        print('%s Creating think time matrix...' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
        
        elastic = ElasticSessionConnection(app_id, tailoring, from_micros, to_micros)
        elastic.scroll_for_sessions(self._append_sessions)
        
        print('%s Think time matrix creation done.' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
    
    def _add_thinktime(self, group_id, from_idx, to_idx, thinktime_micros):
        
        if group_id in self._thinktimes:
            thinktimes = self._thinktimes[group_id]
        else:
            thinktimes = [ array.array('d') for _ in range(self._num_states ** 2) ]
            self._thinktimes[group_id] = thinktimes
        
        idx = from_idx * self._num_states + to_idx
        thinktimes[idx].append(thinktime_micros)
    
    def _append_sessions(self, session_list):
        
        for session in session_list:
            group_id = session['group-id']
            
            endpoints = [ r['endpoint'] for r in session['requests'] ]
            indices = self.label_encoder.transform(endpoints)
            
            start_micros = [ r['start-micros'] for r in session['requests'] ]
            end_micros = [ r['end-micros'] for r in session['requests'] ]
            
            for (from_idx, to_idx, think_start, think_end) in zip(indices, indices[1:], end_micros, start_micros[1:]):
                self._add_thinktime(group_id, from_idx, to_idx, think_end - think_start)
            
            # if there is only one state
            if len(indices) == 1:
                self._add_thinktime(group_id, indices[0], indices[0], 0)
    
    def _thinktime_mean(self, thinktimes):
        if len(thinktimes) == 0:
            return 0
        else:
            return np.mean(np.frombuffer(thinktimes, dtype=np.float64))
    
    def _thinktime_variance(self, thinktimes):
        if len(thinktimes) == 0:
            return 0
        else:
            return np.var(np.frombuffer(thinktimes, dtype=np.float64))
    
    def mean_1d_dict(self):
        """
        Returns the mean values of the collected think times as dict of 1d arrays.
        :return: The think time means per transition.
        """
        
        result_dict = {}
        
        for beh_id, thinktimes in self._thinktimes.items():
            result_dict[beh_id] = [ self._thinktime_mean(tt) for tt in thinktimes ]
        
        return result_dict
    
    def variance_1d_dict(self):
        """
        Returns the variances of the collected think times as dict of 1d arrays.
        :return: The think time variances per transition.
        """
        
        result_dict = {}
        
        for beh_id, thinktimes in self._thinktimes.items():
            result_dict[beh_id] = [ self._thinktime_variance(tt) for tt in thinktimes ]
        
        return result_dict
