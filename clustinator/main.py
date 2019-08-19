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
        # Input data
        data_input = Input(self.sessions_file)
        epsilon, min_samples = data_input.cluster_param()
        session, states = data_input.sessions()

        print('load data done', datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

        # Compute transition matrix next
        markov_chain = MarkovChain(session, states)
        markov_chain = markov_chain.csr_sparse_matrix()

        print('matrix done', datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        print('start clustering')

        # DBSCAN
        dbscan = Clustering(markov_chain, epsilon, min_samples)
        unique, counts, labels = dbscan.unique_labels()
        print("Cluster-Infos:",unique, counts, labels)
        print("End clustering", datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

        # Previouse data
        #prev_markov_chains = data_input.get_prev_markov_chain()
        try:
            prev_markov_chains = data_input.get_prev_markov_chain()
            first_dict = {int(k): v for k, v in prev_markov_chains.items()}
            load_labels = np.array(first_dict.keys())
            header = data_input.get_header()
            app_id = data_input.get_app_id()

            # Backprop
            cluster_dict = dbscan.cluster_dict(labels, markov_chain)

            second_list = dbscan.list_cluster(cluster_dict, labels, load_labels)

            cluster_mean = ca(first_dict, second_list).cluster_backprob()

            # Producer
            cluster_mean = {k: v.tolist() for k, v in cluster_mean.items()}
            message = Message(header, cluster_mean, states).build_json()
            Producer(message, app_id)
        except AttributeError:
            header = data_input.get_header()
            app_id = data_input.get_app_id()
            cluster_dict = dbscan.cluster_dict(labels, markov_chain)
            first_cluster = dbscan.first_cluster(cluster_dict, labels)

            first_cluster = {k: v.tolist() for k, v in first_cluster.items()}
            message = Message(header, first_cluster, states).build_json()
            Producer(message, app_id)

        end_time = datetime.now()
        print('Duration: {}'.format(end_time - start_time))

if __name__ == '__main__':
    # Data imports
    PATH = "../poc/data/new_data/"
    sessions_file = (PATH + 'clustinator-input.json')
    Main(sessions_file).start()
