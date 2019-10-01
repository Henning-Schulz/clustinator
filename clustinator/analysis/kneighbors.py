'''
@author: Henning Schulz
'''

import io
from PIL import Image
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import time
from datetime import datetime

from input import Input
from markovchain import MarkovChain

class KNeighbors:
    
    def __init__(self, json_input):
        """
        Class for estimating the epsilon for DBSCAN using the k-nearest neighbors graph.
        :param json_input: The json input received
        """
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Preparing for knn distance plot creation...')
        
        data_input = Input(json_input)
        session, states = data_input.sessions()
        
        markov_chain = MarkovChain(session, states)
        markov_chain, _ = markov_chain.csr_sparse_matrix()
        
        _, min_samples = data_input.cluster_param()
        
        nbrs = NearestNeighbors(n_neighbors=min_samples).fit(markov_chain)
        distances, _ = nbrs.kneighbors(markov_chain)
        
        self.min_samples = min_samples
        self.distances = sorted(distances[:,min_samples-1])
        self.n = len(states) - 1
        self.title = data_input.get_app_id()
    
    def distance_plot(self):
        """
        Calculates the knn distance plot.
        :return: The distance plot as pdf image
        """
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Creating the distance plot...')
        
        plt.figure()
        _, ax = plt.subplots()
        
        ax.set_title(self.title)
        
        ax.plot(self.distances)
        ax.set_ylabel('%r-dist' % self.min_samples)
        
        def eps2att(x):
            return x / self.n
        
        def att2eps(x):
            return self.n * x
        
        secax = ax.secondary_yaxis('right', functions=(eps2att, att2eps))
        secax.set_ylabel('avg transition tolerance')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='pdf')
        buf.seek(0)
        
        image = buf.read()
        buf.close()
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Distance plot created.')
        
        return image
