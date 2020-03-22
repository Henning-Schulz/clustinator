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
        thinktimes[idx].append(thinktime_micros / 1000) # think times are in milliseconds
    
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
    
    def _recalculate_mean(self, new_mean, new_num_sessions, prev_mean, prev_num_sessions):
        weighted_prev = [ prev_num_sessions * x for x in prev_mean ]
        weighted_new = [ new_num_sessions * x for x in new_mean ]
        absolute = [ sum(x) for x in zip(weighted_prev, weighted_new) ]
        
        total_num_sessions = prev_num_sessions + new_num_sessions
        
        return [ x / total_num_sessions for x in absolute ]
    
    def _recalculate_variance(self, new_variance, new_num_sessions, prev_variance, prev_num_sessions):
        prev_weight = prev_num_sessions ** 2
        new_weight = new_num_sessions ** 2
        
        weighted_prev = [ prev_weight * x for x in prev_variance ]
        weighted_new = [ new_weight * x for x in new_variance ]
        absolute = [ sum(x) for x in zip(weighted_prev, weighted_new) ]
        
        total_weight = (prev_num_sessions + new_num_sessions) ** 2
        
        return [ x / total_weight for x in absolute ]
    
    def mean_1d_dict(self, prev_behavior_model=None, new_num_sessions=None):
        """
        Returns the mean values of the collected think times as dict of 1d arrays.
        :param prev_behavior_model: The previous behavior model. If not None, the think time means will be merged.
        :param new_num_sessions: The number of sessions per new cluster. Needed if prev_behavior_model is not None.
        :return: The think time means per transition.
        """
        
        result_dict = {}
        
        if prev_behavior_model:
            print('%s Merging the previous think time means.' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
            prev_means = prev_behavior_model.think_time_means_1d_dict(self.label_encoder)
            prev_num_sessions = prev_behavior_model.get_num_sessions()
        
        for beh_id, thinktimes in self._thinktimes.items():
            new_mean = [ self._thinktime_mean(tt) for tt in thinktimes ]
            
            if prev_behavior_model:
                result_dict[beh_id] = self._recalculate_mean(new_mean, new_num_sessions[beh_id], prev_means.get(beh_id, new_mean), prev_num_sessions.get(beh_id, 0))
            else:
                result_dict[beh_id] = new_mean
        
        if prev_behavior_model:
            for (old_mid, old_mean) in prev_means.items():
                if old_mid not in result_dict:
                    result_dict[old_mid] = old_mean
                    print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Added old think time mean of group', old_mid, 'as no new session belongs to it.')
        
        return result_dict
    
    def variance_1d_dict(self, prev_behavior_model=None, new_num_sessions=None):
        """
        Returns the variances of the collected think times as dict of 1d arrays.
        :return: The think time variances per transition.
        """
        
        result_dict = {}
        
        if prev_behavior_model:
            print('%s Merging the previous think time variances.' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
            prev_variances = prev_behavior_model.think_time_variances_1d_dict(self.label_encoder)
            prev_num_sessions = prev_behavior_model.get_num_sessions()
        
        for beh_id, thinktimes in self._thinktimes.items():
            new_variance = [ self._thinktime_variance(tt) for tt in thinktimes ]
            
            if prev_behavior_model:
                result_dict[beh_id] = self._recalculate_variance(new_variance, new_num_sessions[beh_id], prev_variances.get(beh_id, new_variance), prev_num_sessions.get(beh_id, 0))
            else:
                result_dict[beh_id] = new_variance
        
        if prev_behavior_model:
            for (old_mid, old_variance) in prev_variances.items():
                if old_mid not in result_dict:
                    result_dict[old_mid] = old_variance
                    print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Added old think time variance of group', old_mid, 'as no new session belongs to it.')
        
        return result_dict
    
