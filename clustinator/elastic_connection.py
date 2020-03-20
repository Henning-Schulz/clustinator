'''
@author: Henning Schulz
'''

import time
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionTimeout
import requests
from time import sleep

class ElasticConnection:
    
    _es = None
    _host = None
    _timeout = None
    
    @staticmethod
    def init(host, timeout=10):
        ElasticConnection._timeout = timeout
        ElasticConnection._host = host
        ElasticConnection._es = Elasticsearch(host, timeout=timeout)


class ElasticSessionConnection(ElasticConnection):
    
    def __init__(self, app_id, tailoring, from_micros, to_micros):
        if ElasticConnection._es is None:
            print('Elasticsearch connection not initialized!')
            exit() 
        
        self.index = '%s.%s.sessions' % (app_id, tailoring)
        self.from_micros = from_micros
        self.to_micros = to_micros
        
        if not ElasticConnection._es.indices.exists(index=self.index):
            print('Index ' + self.index + ' not exists')
            exit()
    
    def _query(self):
        return {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "start-micros": {
                                        "from": self.from_micros,
                                        "to": self.to_micros,
                                        "include_lower": False,
                                        "include_upper": True
                                    }
                                }
                            }
                        ]
                    }
                }
    
    def get_unique_endpoints(self):
        """
        Calculates and returns the unique endpoints ocurring in any of the sessions in the specified range.
        :return: The list of endpoints.
        """
        
        print('%s Getting unique endpoints in %r...' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), self.index))
        
        response = ElasticConnection._es.search(
            index = self.index,
            body = {
                "size": 0,
                "query": self._query(),
                "aggs": {
                    "endpoints": {
                        "terms": {
                            "field": "requests.endpoint",
                            "size": 1000
                        }
                    }
                }
            }
        )
        
        print('%s Returning %i unique endpoints.' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), len(response['aggregations']['endpoints']['buckets'])))
        
        return [d['key'] for d in response['aggregations']['endpoints']['buckets']]
    
    def scroll_for_sessions(self, callback):
        """
        Scrolls for the sessions in the specified range for the specified app_id and tailoring
        and calls a callback for each retrieved chunk.
        :param callback: Callback to be called for each chunk. Should consume a list of sessions.
        """
        
        print('%s Scrolling for sessions in %r...' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), self.index))
        
        response = ElasticConnection._es.search(
            index = self.index,
            scroll = '5m',
            body = {
                "size": 2500,
                "_source": {
                    "excludes": [ "requests.extended-information", "requests.flags" ]
                },
                "query": self._query(),
                "sort": [
                    {
                        "start-micros": { "order": "asc" }
                    }
                ]
            }
        )
        
        sid = response['_scroll_id']
        scroll_size = len(response['hits']['hits'])
        scroll_num = 1
        
        while scroll_size > 0:
            print('%s Scroll %r: Processing %r elements...' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), scroll_num, scroll_size))
            
            callback([ d['_source'] for d in response['hits']['hits']])
            
            print('%s Scroll %r: Processing done. Retrieving next documents...' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), scroll_num))
            
            response = ElasticConnection._es.scroll(scroll_id = sid, scroll = '5m')
            
            sid = response['_scroll_id']
            scroll_size = len(response['hits']['hits'])
            scroll_num += 1
        
        print('%s Reached the end of the scroll.' % datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        ElasticConnection._es.clear_scroll(scroll_id = sid)
    
    def set_group_ids(self, group_id, session_ids):
        """
        Sets the group-id property in the sessions stored in Elasticsearch.
        :param group_id: The group-id.
        :param session_ids: The IDs of the sessions to be tagged with the group-id as list.
        """
        
        print('%s Updating the group-id %r of the sessions in %r...' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), group_id, self.index))
        
        response = None
        
        while not response:
            try:
                response = ElasticConnection._es.update_by_query(
                    index = self.index,
                    conflicts = 'proceed',
                    wait_for_completion = False,
                    refresh = True,
                    body = {
                        "script": {
                            "source": "ctx._source.put(\"group-id\", params.group_id)",
                            "lang": "painless",
                            "params": { "group_id": group_id }
                        },
                        "query": {
                            "ids": { "values": session_ids }
                        }
                    }
                )
            except (ConnectionTimeout, ConnectionError) as e:
                print('%s WARN Update by query request failed! %r. Retrying after %r seconds...' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), str(e), ElasticConnection._timeout))
                sleep(ElasticConnection._timeout)
        
        task_id = response['task']
        
        print('%s Got the task ID %r.' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), task_id))
        
        completed = False
        
        while not completed:
            print('%s Waiting (another) %r seconds for completion...' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), ElasticConnection._timeout))
            
            try:
                task_response = ElasticConnection._es.tasks.get(task_id=task_id, timeout=str(ElasticConnection._timeout) + 's', wait_for_completion=True)
                completed = task_response['completed']
            except (ConnectionTimeout, ConnectionError) as e:
                print('%s WARN Wait request failed! %r. Retrying...' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), str(e)))
                completed = False
        
        print('%s Task %r completed! Updated %i of %i sessions' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), task_id, task_response['task']['status']['updated'], task_response['task']['status']['total']))
        
        requests.delete('http://' + ElasticConnection._host + ':9200/.tasks/task/' + task_id)


class ElasticBehaviorConnection(ElasticConnection):
    
    def __init__(self, app_id, tailoring, before_micros):
        if ElasticConnection._es is None:
            print('Elasticsearch connection not initialized!')
            exit() 
        
        self.index = '%s.%s.behavior' % (app_id, tailoring)
        self.before_micros = before_micros
    
    def get_latest(self, n = 1):
        """
        Searches for the latest n behavior model before the specified date.
        :param n: Number of behavior models to be returned at most. Defaults to 1.
        :return: The latest behavior model or None, if there is none.
        """
        
        if not ElasticConnection._es.indices.exists(index=self.index):
            print('Index ' + self.index + ' not exists')
            return []
        
        print('%s Getting the latest behavior model in %r...' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), self.index))
        
        response = ElasticConnection._es.search(
            index = self.index,
            body = {
                "size": n,
                "query": {
                    "range": {
                        "timestamp": {
                            "to": self.before_micros / 1000,
                            "include_upper": False
                        }
                    }
                },
                "sort": [
                    {
                        "timestamp": { "order": "desc" }
                    }
                ]
            }
        )
        
        hits = response['hits']['hits']
        
        if len(hits) == 0:
            print('%s Could not find any behavior models.' % datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
            return []
        else:
            print('%s Returning the %d latest behavior model.' % (datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), len(hits)))
            return [ d['_source'] for d in hits]
        
        

if __name__ == '__main__':
    ElasticConnection.init('localhost')
    con = ElasticSessionConnection('sis', 'all', 0, 2527728400000000)
    
    endpoints = con.get_unique_endpoints()
    print(endpoints)
    
    def session_callback(result):
        for session in result:
            print([ r['endpoint'] for r in session['requests'] ])
    
    sessions = con.scroll_for_sessions(session_callback)
    

