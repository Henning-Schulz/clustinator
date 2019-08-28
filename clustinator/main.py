'''
@author: An Dang, Henning Schulz
'''

import time
from datetime import datetime
import numpy as np

from input import Input
from markovchain import MarkovChain
from clustering import Clustering
from analysis.cluster_analysis import Cluster_analysis as ca
from producer import Producer
from message import Message

class Main:
    def __init__(self, sessions_file):
        self.sessions_file = sessions_file

    def start(self):
        start_time = datetime.now()

        data_input = Input(self.sessions_file)
        epsilon, min_samples = data_input.cluster_param()
        session, states = data_input.sessions()
        header = data_input.get_header()
        app_id = data_input.get_app_id()

        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Clustering for app-id', app_id)

        print('Creating the sparse matrices...')
        markov_chain = MarkovChain(session, states)
        markov_chain, session_ids = markov_chain.csr_sparse_matrix()

        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Matrix creation done. Starting the clustering...')

        dbscan = Clustering(markov_chain, epsilon, min_samples)
        unique, counts, labels = dbscan.label_summary()
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Clustering done. Found the following clusters:', unique, 'with counts:', counts)
        
        print("Calculating the cluster means...")
        cluster_means = dbscan.cluster_means()
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Mean calculation done. Grouping the session IDs by cluster label...')
        
        prev_markov_chains = data_input.get_prev_markov_chain()
        
        if prev_markov_chains == None:
            print('There are no previous markov chains.')
            clustered_sessions = ca.sessions_per_cluster(labels, session_ids, None)
        else:
            print('Mapping to the previous markov chains...')
            cluster_analysis = ca(prev_markov_chains, cluster_means)
            cluster_mapping = cluster_analysis.cluster_mapping()
            cluster_means = cluster_analysis.relabel_clusters(cluster_mapping)
            print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Calculated mapping:', cluster_mapping)
            
            clustered_sessions = ca.sessions_per_cluster(labels, session_ids, cluster_mapping)
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Session ID grouping done. Returning the result...')

        message = Message(header, cluster_means, states, clustered_sessions).build_json()
        Producer(message, app_id)

        end_time = datetime.now()
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Clustering for app-id', app_id, 'done. Took', (end_time - start_time))


if __name__ == '__main__':
    # Data imports
    PATH = "../poc/data/new_data/"
    sessions_file = (PATH + 'clustinator-input.json')
    Main(sessions_file).start()
