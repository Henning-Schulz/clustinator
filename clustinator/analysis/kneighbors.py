'''
@author: Henning Schulz
'''

import io
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import time
from datetime import datetime
import numpy as np

from input import Input
from session_matrix import SessionMatrix
from session_matrix_creator import SessionMatrixCreator

class KNeighbors:
    
    def __init__(self, json_input):
        """
        Class for estimating the epsilon for DBSCAN using the k-nearest neighbors graph.
        :param json_input: The json input received
        """
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Preparing for knn distance plot creation...')
        
        data_input = Input(json_input)
        app_id = data_input.get_app_id()
        tailoring = data_input.get_tailoring()
        start_micros, _, end_micros = data_input.get_range_micros()
        
        matrix_creator = SessionMatrixCreator(app_id, tailoring, start_micros, end_micros, collect_session_ids = False)
        matrix = matrix_creator.create()
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Converting to CSR...')
        csr_matrix = matrix.as_csr_matrix()
        
        _, min_samples = data_input.cluster_param()
        num_sessions = csr_matrix.get_shape()[0]
        
        if min_samples > num_sessions:
            print('Using min sample size %d (number of sessions) instead of %d (configured).' % (num_sessions, min_samples))
            min_samples = num_sessions
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Calculating the distances...')
        
        self.ks = tuple(filter(lambda x : x <= num_sessions, ( min_samples//10, min_samples//2, min_samples, min_samples*2, min_samples*10 )))
        self.styles = ( '--c', '-c', '-b', '-k', '--k' )[:len(self.ks)]
        self.linewidths = ( 0.7, 0.7, 1.2, 0.7, 0.7 )[:len(self.ks)]
        self.distances = { k: [] for k in self.ks }
        
        nbrs = NearestNeighbors(n_neighbors=max(self.ks)).fit(csr_matrix)
        print_steps = [ int(round(s)) for s in np.linspace(0, num_sessions-1, num = 11) ]
        
        for i in range(num_sessions):
            distances, _ = nbrs.kneighbors(csr_matrix.getrow(i))
            
            for k in self.ks:
                self.distances[k].append(distances[0,k-1])
            
            if i in print_steps:
                print('progress: %d%%' % round(i / num_sessions * 100))
        
        print('')
        
        self.n = len(matrix.states()) - 1
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
        
        for k, style, width in zip(self.ks, self.styles, self.linewidths):
            ax.plot(sorted(self.distances[k]), style, label = '%r-dist' % k, linewidth = width)
        
        ax.set_ylabel('knn dist')
        ax.legend(loc='upper left')
        
        def eps2att(x):
            return x / self.n
        
        def att2eps(x):
            return self.n * x
        
        secax = ax.secondary_yaxis('right', functions=(eps2att, att2eps))
        secax.set_ylabel('avg transition tolerance')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='pdf', bbox_inches='tight')
        buf.seek(0)
        
        image = buf.read()
        buf.close()
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Distance plot created.')
        
        return image
