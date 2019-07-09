import numpy as np
import pandas as pd
from sklearn import preprocessing
from scipy.sparse import csr_matrix


class MarkovChain:

    def __init__(self, sessions, states):
        self.sessions = sessions
        self.states = states

    def encoding_factorize(self, session_value):
        """
        Label encoding the data and return factorize session value.
        :return: Factorize session value
        """
        le = preprocessing.LabelEncoder()
        le.fit(session_value)
        le.transform(session_value)

        return pd.factorize(session_value)[0]

    def markov_chain(self, encoding_factorize):
        """
        Compute a markov chain from the session, the matrix is as big as the session.
        :param encoding_factorize: Need the factorize session
        :return: num. of states and the probability matrix
        """
        num_states = 1 + max(encoding_factorize)
        matrix = [[0] * num_states for _ in range(num_states)]

        for (i, j) in zip(encoding_factorize, encoding_factorize[1:]):
            matrix[i][j] += 1

        for row in matrix:
            s = sum(row)
            if s > 0:
                row[:] = [f / s for f in row]

        return num_states, matrix

    def transition_matrix(self, value, matrix, num_states):
        """
        Transfer the matrix into a Markov chain with implementing the states.
        :param value: values from the the raw session
        :param matrix: the compute matrix from the session
        :param num_states: num. states from the compute matrix
        :return: return a flatten vector of the matrix
        """
        # unique array in the right order
        value = np.array(value)
        _, idx = np.unique(value, return_index=True)

        df = pd.DataFrame(data=matrix, index=value[np.sort(idx)],
                          columns=value[np.sort(idx)])

        df_1 = pd.DataFrame(index=self.states, columns=self.states, dtype='float64')
        df_1.update(df, join='left')

        merge = pd.concat([pd.concat([df_1, df], axis=1, sort=False)], axis=0).fillna(0).round(2).iloc[:, :-num_states]

        return np.array(merge.values.flatten().tolist())

    def csr_sparse_matrix(self):
        """
        TODO: Incremental sparse matrix
        Convert the flatten markov chain into a csr sparse matrix
        :return: csr sparse matrix for the clustering
        """
        markovchains = []

        for key, value in self.sessions.items():
            encoding = self.encoding_factorize(value)

            num_states, matrix = self.markov_chain(encoding)

            transition_matrix = self.transition_matrix(value, matrix, num_states)

            markovchains.append(transition_matrix)

        return csr_matrix(markovchains)
