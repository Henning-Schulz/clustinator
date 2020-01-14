'''
@author: An Dang, Henning Schulz
'''

import time
from datetime import datetime
import pika
import numpy as np

from input import Input
from session_matrix_creator import SessionMatrixCreator
from session_matrix_buffer import session_matrix_buffer_noop
from analysis.cluster_analysis import Cluster_analysis as ca
from producer import Producer
from message import Message
from behavior_model import BehaviorModel
from behavior_model_creator import BehaviorModelCreator
from elastic_connection import ElasticConnection
from thinktime_matrix import ThinktimeMatrix
from dbscan_appender import DbscanAppender
from kmeans_appender import KmeansAppender
from minimum_distance_appender import MinimumDistanceAppender

class Main:
    def __init__(self, sessions_file, rabbitmq_host = 'localhost', rabbitmq_port = pika.ConnectionParameters.DEFAULT_PORT, matrix_buffer = session_matrix_buffer_noop, fast_test = False):
        self.sessions_file = sessions_file
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port
        self.matrix_buffer = matrix_buffer
        self.fast_test = fast_test

    def start(self):
        start_time = datetime.now()

        data_input = Input(self.sessions_file)
        avg_tolerance, epsilon, min_samples = data_input.dbscan_param()
        k, n_jobs = data_input.kmeans_param()
        header = data_input.get_header()
        app_id = data_input.get_app_id()
        tailoring = data_input.get_tailoring()
        start_micros, interval_start_micros, end_micros = data_input.get_range_micros()
        lookback = data_input.get_lookback()
        append_strategy = data_input.get_append_strategy()
        dimensions = data_input.get_dimensions()

        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Clustering for app-id', app_id, 'using', append_strategy,
              'with the following parameters: epsilon =', epsilon, ' avg_tolerance =', avg_tolerance, ' min-sample-size =', min_samples, ' k =', k,
              ' n_jobs =', n_jobs, ' dimensions =', dimensions)
        print('Clustering range is', start_micros, '-', interval_start_micros, '-', end_micros)
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Loading previous Markov chains...')
        prev_behavior_models = BehaviorModelCreator(app_id, tailoring, interval_start_micros).load(lookback)
        
        if not prev_behavior_models:
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'There are no previous Markov chains.')
        else:
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Found and loaded previous Markov chains.')
        
        matrix = self.matrix_buffer.load(app_id, tailoring, start_micros, end_micros)
        matrix_creator = SessionMatrixCreator(app_id, tailoring, start_micros, end_micros)
        
        if matrix:
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Reusing the buffered session matrix.')
        else:
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Loading the session matrix from elasticsearch...')
            prev_endpoints = set.union(*map(BehaviorModel.get_endpoints, prev_behavior_models)) if prev_behavior_models else set()
            matrix = matrix_creator.create(list(prev_endpoints))
            
            self.matrix_buffer.store(app_id, tailoring, start_micros, end_micros, matrix)
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Converting to CSR...')
        csr_matrix = matrix.as_csr_matrix()
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Matrix creation done.')
        
        appenders = {'dbscan': DbscanAppender(epsilon, avg_tolerance, matrix.states(), min_samples, prev_behavior_models, matrix.label_encoder),
                     'kmeans': KmeansAppender(prev_behavior_models, k, n_jobs, dimensions),
                     'minimum-distance': MinimumDistanceAppender(prev_behavior_models, matrix.label_encoder, dimensions)}
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Appending the new sessions using', append_strategy)
        
        appender = appenders[append_strategy]
        appender.append(csr_matrix)
        cluster_means = appender.cluster_means
        labels = appender.labels
        cluster_mapping = appender.cluster_mapping
        num_sessions = appender.num_sessions
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Appending done. Grouping the session IDs...')
            
        clustered_sessions = ca.sessions_per_cluster(labels, matrix.session_ids, cluster_mapping)
        matrix_creator.update_group_ids(clustered_sessions)
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Session ID grouping done.')
        
        if not self.fast_test:
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Calculating the think times...')
            thinktime_matrix = ThinktimeMatrix(app_id, tailoring, start_micros, end_micros, matrix.label_encoder)
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Think time calculation done. Returning the result...')

        total_num_sessions = np.sum([ count for _, count in num_sessions.items() ])
        frequency = { beh_id: count / total_num_sessions for beh_id, count in num_sessions.items() }
        
        if not self.fast_test:
            message = Message(header, cluster_means, matrix.states().tolist(), thinktime_matrix.mean_1d_dict(), thinktime_matrix.variance_1d_dict(), frequency, num_sessions).build_json()
        else:
            message = Message(header, cluster_means, matrix.states().tolist(), cluster_means, cluster_means, frequency, num_sessions).build_json()

        Producer(app_id, self.rabbitmq_host, self.rabbitmq_port).send_clustering(message)

        end_time = datetime.now()
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Clustering for app-id', app_id, 'done. Took', (end_time - start_time))


if __name__ == '__main__':
    ElasticConnection.init('localhost')
    sessions_file = open('../poc/data/sis-input.json')
    Main(sessions_file.read()).start()
