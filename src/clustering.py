from sklearn.cluster import DBSCAN
import numpy as np
import datetime
import time

from input import Input
from markovchain import MarkovChain


states = ["INITIAL","login","View_Items","home","logout","View_Items_quantity","Add_to_Cart","shoppingcart",
          "remove","deferorder","purchasecart","inventory","sellinventory","clearcart","cancelorder","$"]

# Data imports
PATH = "../data/raw/"
sessions_file = (PATH+'sessions.dat')


class Clustering:
    def __init__(self, X):
        self.X = X

    def dbscan(self):

        return DBSCAN(eps=1.5, min_samples=10).fit(self.X)

    def unique_labels(self):
        labels = self.dbscan().labels_
        unique, counts = np.unique(labels, return_counts=True)
        return unique, counts

    def compare_results(self):
        unique, counts = self.unique_labels()
        # represent the cluster results as dict
        result = dict(zip(unique, counts))

        return result

# main-method
if __name__ == '__main__':
    # Input data
    input = Input(sessions_file)

    start, stop = None, 1000
    past_step_size = 1000
    steps = 5
    for _ in enumerate(range(steps)):
        if _ == (0, 0):
            pass
        else:
            start += 1000
            stop += 1000

        # Slice sessions @sessions(None, None)
        current_step = input.sessions(start, stop)

        if _ >= (1, 1):
            past_start = (start-past_step_size)
            past_stop = (stop-past_step_size)
            past_step = input.sessions(past_start, past_stop)

            print('load data done', datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))


            """
            To Do's:
            Change the parameter names!!!
            """
            # Compute transition matrix
            mc = MarkovChain(session, states)
            mc = mc.transition_matrix()

            print('matrix done', datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
            print('start clustering \n')

            # DBSCAN
            dbscan = Clustering(mc)

            print("\nEnd clustering", datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

            """# Compute the clustering compromise
            result1 = dbscan.compare_results()
            result2 = dbscan.compare_results()
            
            diff_dict = {}
            tmp = []
            
            for key in result1:
                tmp.append(key)
                if key in result2:
                    diff_dict[key] = (result1[key] - result2[key])
        
            if len(tmp) != len(result2):
                for key in result2:
                    if key not in result1.keys():
                        diff_dict[key] = result2[key]"""
