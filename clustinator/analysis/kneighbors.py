'''
@author: Henning Schulz
'''

import io
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import time
from datetime import datetime

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
        
        print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), 'Calculating the distances...')
        
        nbrs = NearestNeighbors(n_neighbors=min_samples*10).fit(csr_matrix)
        distances, _ = nbrs.kneighbors(csr_matrix)
        
        self.min_samples = min_samples
        self.distances = sorted(distances[:,min_samples-1])
        self.distances_by_2 = sorted(distances[:,min_samples//2-1])
        self.distances_by_10 = sorted(distances[:,min_samples//10-1])
        self.distances_times_2 = sorted(distances[:,min_samples*2-1])
        self.distances_times_10 = sorted(distances[:,min_samples*10-1])
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
        
        ax.plot(self.distances_by_10, '--c', label = '%r-dist' % (self.min_samples//10), linewidth = 0.7)
        ax.plot(self.distances_by_2, '-c', label = '%r-dist' % (self.min_samples//2), linewidth = 0.7)
        ax.plot(self.distances, '-b', label = '%r-dist' % self.min_samples, linewidth = 1.2)
        ax.plot(self.distances_times_2, '-k', label = '%r-dist' % (self.min_samples*2), linewidth = 0.7)
        ax.plot(self.distances_times_10, '--k', label = '%r-dist' % (self.min_samples*10), linewidth = 0.7)
        ax.set_ylabel('dist')
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
