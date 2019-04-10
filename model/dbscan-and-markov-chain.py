import re
import numpy as np
import pandas as pd
from sklearn import preprocessing
from scipy.sparse import csr_matrix
from sklearn.cluster import DBSCAN
from sklearn import metrics


states = ["INITIAL","login","View_Items","home","logout","View_Items_quantity","Add_to_Cart","shoppingcart",
          "remove","deferorder","purchasecart","inventory","sellinventory","clearcart","cancelorder","$"]

#Data imports
PATH = "../data/raw/"
sessions_file = (PATH+'sessions.dat')
#Dict of sessions
with open(sessions_file) as fn:
    sessions_raw = fn.readlines()

def session_request_dict(sessions_raw):
    s_r_dict = {}
    for session in sessions_raw:
        key = re.search('([^.]+)', session).group()
        value = re.findall('\"(.*?)\"', session)
        s_r_dict[key] = value

    return s_r_dict


def transition_matrix(sessions, states):
    markovchains = []
    for key, value in sessions.items():
        # labelEncoding
        le = preprocessing.LabelEncoder()
        le.fit(value)
        transformed_s = le.transform(value)

        # factorize
        factorize = pd.factorize(value)[0]

        # matrix
        n = 1 + max(factorize)  # number of states
        M = [[0] * n for _ in range(n)]

        for (i, j) in zip(factorize, factorize[1:]):
            M[i][j] += 1

        # now convert to probabilities:
        for row in M:
            s = sum(row)
            if s > 0:
                row[:] = [f / s for f in row]

        # unique array in the right order
        value = np.array(value)
        _, idx = np.unique(value, return_index=True)

        df = pd.DataFrame(data=M, index=value[np.sort(idx)],
                          columns=value[np.sort(idx)])

        df_1 = pd.DataFrame(index=states, columns=states, dtype='float64')

        merge = df_1.update(df, join='left')
        merge = pd.concat([pd.concat([df_1, df], axis=1, sort=False)], axis=0).fillna(0).round(2).iloc[:, :-n]

        # convert into Vector
        merge = np.array(merge.values.flatten().tolist())
        # 2-D array
        markovchains.append(merge)
        # csr sparse matrix
        csr = csr_matrix(markovchains)



    return csr

data = session_request_dict(sessions_raw)
print('load data done')
X = transition_matrix(data, states)
print('matrix done')
print('start clustering')
clustering = DBSCAN(eps=1000, min_samples=1000).fit(X)
labels = clustering.labels_
#print(labels)
print(np.unique(labels, return_counts=True))
print(clustering)