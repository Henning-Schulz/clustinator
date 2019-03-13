#!/usr/bin/env python

"""
Description of script.
"""

from sklearn import preprocessing
from scipy.sparse import coo_matrix
import numpy as np
import pandas as pd
import re

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import column_or_1d

class MyLabelEncoder(LabelEncoder):

    def fit(self, y):
        y = column_or_1d(y, warn=True)
        self.classes_ = pd.Series(y).unique()
        return self

sessions = {'HZKS0-WG8pZr0eCsZlBAP5Xm': ['1-Initial','2-login',
   '3-View_Items',
   '3-View_Items',
    '3-View_Items',
    '3-View_Items',
    '3-View_Items',
    '3-View_Items',
    '3-View_Items',
    '3-View_Items',
    '3-View_Items',
    '3-View_Items',
    '3-View_Items',
    '3-View_Items',
    '3-View_Items',
    '3-View_Items',
   '4-home',
   '5-logout', '6-$']}

sessions_1 = {'HZKS0-WG8pZr0eCsZlBAP5Xm': ['login',
   'View_Items',
   'View_Items',
   'View_Items',
   'View_Items',
   'View_Items',
   'View_Items',
   'View_Items',
   'View_Items',
   'View_Items',
   'View_Items',
   'View_Items',
   'View_Items',
   'View_Items',
   'View_Items',
   'home',
   'logout'],'5tPgZbHdK2Zp+heFBs8HsMkx': ['login',
   'View_Items_quantity',
   'Add_to_Cart',
   'View_Items_quantity',
   'Add_to_Cart',
   'View_Items_quantity',
   'Add_to_Cart',
   'View_Items_quantity',
   'Add_to_Cart',
   'View_Items_quantity',
   'Add_to_Cart',
   'shoppingcart',
   'remove',
   'shoppingcart',
   'remove',
   'shoppingcart',
   'remove',
   'shoppingcart',
   'remove',
   'deferorder',
   'home',
   'logout']}

"""
def transition_matrix(transitions):
    n = 1+max(transitions) #number of states

    M = [[0]*n for _ in range(n)]

    for (i,j) in zip(transitions,transitions[1:]):
        M[i][j] += 1

    #now convert to probabilities:
    for row in M:
        s = sum(row)
        if s > 0:
            row[:] = [f/s for f in row]
    return M

#test:

t = [1,1,2,6,8,5,5,7,8,8,1,1,4,5,5,0,0,0,1,1,4,4,5,1,3,3,4,5,4,1,1]
print(max(t))
m = transition_matrix(t)
for row in m: print(' '.join('{0:.2f}'.format(x) for x in row))
print(m)
"""

def pars(sessions):

    for key in sessions:
        item_list = []
        # Unique values
        #print(len(sessions[key]))

        for item in sessions[key]:
            # items per session
            if item in item_list:
                pass
            else:
                item_list.append(item)
        print(item_list)
        print('len:',len(item_list))


def transition_matrix(sessions):
    #t = [1, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 5, 0]
    #[0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 4, 5]
    for k in sessions:
        s = sessions_1[k]
        le = preprocessing.LabelEncoder()
        #le = MyLabelEncoder()
        le.fit(s)
        transformed_s = le.transform(s)
        print(transformed_s)

        test = pd.factorize(s)[0]
        print("test",test)

        n = 1 + max(test)  # number of states
        M = [[0] * n for _ in range(n)]

        for (i, j) in zip(test, test[1:]):
            M[i][j] += 1
            #print(M)
        # now convert to probabilities:
        for row in M:
            #print(row)
            s = sum(row)
            #print(s)
            if s > 0:
                row[:] = [f / s for f in row]

        return M

        #coo = coo_matrix((test,(M[i],M[j])), shape=(4, 4))
        #return coo




def main():
    #pars(sessions)
    m = transition_matrix(sessions)
    for row in m: print(' '.join('{0:.2f}'.format(x) for x in row))


if __name__ == '__main__':
    main()