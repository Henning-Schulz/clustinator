import numpy as np
import pandas as pd
from sklearn import preprocessing
from scipy.sparse import csr_matrix


class MarkovChain:

    def __init__(self, sessions, states):
        self.sessions = sessions
        self.states = states

    def transition_matrix(self):
        markovchains = []

        for key, value in self.sessions.items():
            # labelEncoding
            le = preprocessing.LabelEncoder()
            le.fit(value)
            le.transform(value)

            # factorize
            factorize = pd.factorize(value)[0]

            # matrix
            n = 1 + max(factorize)  # number of states
            m = [[0] * n for _ in range(n)]

            for (i, j) in zip(factorize, factorize[1:]):
                m[i][j] += 1

            # now convert to probabilities:
            for row in m:
                s = sum(row)
                if s > 0:
                    row[:] = [f / s for f in row]

            # unique array in the right order
            value = np.array(value)
            _, idx = np.unique(value, return_index=True)

            df = pd.DataFrame(data=m, index=value[np.sort(idx)],
                              columns=value[np.sort(idx)])

            df_1 = pd.DataFrame(index=self.states, columns=self.states, dtype='float64')
            df_1.update(df, join='left')

            merge = pd.concat([pd.concat([df_1, df], axis=1, sort=False)], axis=0).fillna(0).round(2).iloc[:, :-n]

            # convert into Vector
            merge = np.array(merge.values.flatten().tolist())
            # 2-D array
            markovchains.append(merge)
            # csr sparse matrix
            csr = csr_matrix(markovchains)

        return csr
