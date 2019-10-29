'''
@author: An Dang, Henning Schulz
'''

import time
from datetime import datetime
import pika

from input import Input
from session_matrix import SessionMatrix
from session_matrix_creator import SessionMatrixCreator
from clustering import Clustering
from analysis.cluster_analysis import Cluster_analysis as ca
from producer import Producer
from message import Message
from behavior_model import BehaviorModel
from elastic_connection import ElasticConnection
from thinktime_matrix import ThinktimeMatrix

class Main:
    def __init__(self, sessions_file, rabbitmq_host = 'localhost', rabbitmq_port = pika.ConnectionParameters.DEFAULT_PORT):
        self.sessions_file = sessions_file
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_port = rabbitmq_port

    def start(self):
        start_time = datetime.now()

        data_input = Input(self.sessions_file)
        avg_tolerance, min_samples = data_input.cluster_param()
        header = data_input.get_header()
        app_id = data_input.get_app_id()
        tailoring = data_input.get_tailoring()
        start_micros, interval_start_micros, end_micros = data_input.get_range_micros()

        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Clustering for app-id', app_id, 'with avg. transition tolerance', avg_tolerance, 'and min-sample-size', min_samples)

        print('Creating the sparse matrices...')
        matrix_creator = SessionMatrixCreator(app_id, tailoring, start_micros, end_micros)
        matrix = matrix_creator.create()
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Converting to CSR...')
        csr_matrix = matrix.as_csr_matrix()
        epsilon = (len(matrix.states()) - 1) * avg_tolerance

        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Matrix creation done. Starting the clustering with epsilon', epsilon, '...')

        dbscan = Clustering(csr_matrix, epsilon, min_samples)
        unique, counts, labels = dbscan.label_summary()
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Clustering done. Found the following clusters:', unique, 'with counts:', counts)
        
        print("Calculating the cluster means...")
        cluster_means = dbscan.cluster_means()
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Mean calculation done. Grouping the session IDs by cluster label...')
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Loading previous Markov chains...')
        prev_behavior_model = BehaviorModel(matrix.label_encoder, app_id, tailoring, interval_start_micros)
        prev_behavior_model.load_json()
        prev_markov_chains = prev_behavior_model.as_1d_dict()
        
        if prev_markov_chains == None:
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'There are no previous markov chains.')
            clustered_sessions = ca.sessions_per_cluster(labels, matrix.session_ids, None)
        else:
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Mapping to the previous markov chains...')
            cluster_analysis = ca(prev_markov_chains, cluster_means)
            cluster_mapping = cluster_analysis.cluster_mapping()
            cluster_means = cluster_analysis.relabel_clusters(cluster_mapping)
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Calculated mapping:', cluster_mapping)
            
            clustered_sessions = ca.sessions_per_cluster(labels, matrix.session_ids, cluster_mapping)
        
        matrix_creator.update_group_ids(clustered_sessions)
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Session ID grouping done. Calculating the think times...')
        
        thinktime_matrix = ThinktimeMatrix(app_id, tailoring, start_micros, end_micros, matrix.label_encoder)
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Think time calculation done. Returning the result...')

        frequency = { beh_id: len(s) / len(matrix.session_ids) for beh_id, s in clustered_sessions.items() }
        message = Message(header, cluster_means, matrix.states().tolist(), thinktime_matrix.mean_1d_dict(), thinktime_matrix.variance_1d_dict(), frequency).build_json()
        Producer(app_id, self.rabbitmq_host, self.rabbitmq_port).send_clustering(message)

        end_time = datetime.now()
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Clustering for app-id', app_id, 'done. Took', (end_time - start_time))


if __name__ == '__main__':
    ElasticConnection.init('localhost')
    sessions_file = open('../poc/data/sis-input.json')
    Main(sessions_file.read()).start()
