'''
@author: Henning Schulz, An Dang
'''

import array
import numpy as np
from sklearn import preprocessing
from scipy.sparse.csr import csr_matrix

class SessionMatrix:
    
    def __init__(self, states, collect_session_ids = True):
        states.append("INITIAL*")
        states.append("$")
        
        self.label_encoder = preprocessing.LabelEncoder()
        self.label_encoder.fit(states)
        self._final_index = self.label_encoder.transform(["$"])[0]
        
        self.num_states = len(states)
        
        self._indptr = array.array('i', [ 0 ])
        self._indices = array.array('i')
        self._data = array.array('d')
        
        self.session_ids = []
        self.collect_session_ids = collect_session_ids
        
        self._num_added = 0
        
        self._tmp_matrix = [[0] * self.num_states for _ in range(self.num_states)]

    def _populate_markov_chain(self, session):
        """
        Compute a Markov chain from the session and populates the internal transition matrix.
        :param session: The session (list of endpoints) to be transformed to an array.
        """
        
        session.insert(0, "INITIAL*")
        session.append("$")
        
        # reset _tmp_matrix to 0
        for row in range(self.num_states):
            for col in range(self.num_states):
                self._tmp_matrix[row][col] = 0
        
        session__indices = self.label_encoder.transform(session)

        for (i, j) in zip(session__indices, session__indices[1:]):
            self._tmp_matrix[i][j] += 1

        for row in self._tmp_matrix:
            s = sum(row)
            if s > 0:
                for j in range(self.num_states):
                    row[j] = row[j] / s
        
        
        self._tmp_matrix[self._final_index][self._final_index] = 1
    
    def _col_index(self, from_idx, to_idx):
        return from_idx * self.num_states + to_idx
    
    def _add_transition(self, from_idx, to_idx, prob):
        if prob > 0:
            col = self._col_index(from_idx, to_idx)
            
            self._data.append(prob)
            self._indices.append(col)
            self._num_added += 1
    
    def _next_session(self):
        self._indptr.append(self._num_added)
    
    def _append_session(self, session):
        self._populate_markov_chain(session)
        
        for row in range(self.num_states):
            for col in range(self.num_states):
                self._add_transition(row, col, self._tmp_matrix[row][col])
        
        self._next_session()
    
    def append_sessions(self, session_list):
        """
        Append a chunk of sessions.
        :param session_list: The sessions as list in JSON structure.
        """
        
        for session in session_list:
            self._append_session([ r['endpoint'] for r in session['requests'] ])
            
            if self.collect_session_ids:
                self.session_ids.append(session['unique-id'])
    
    def as_csr_matrix(self):
        """
        Gets the created matrix as CSR sparse matrix.
        :return: The CRS matrix
        """
        
        indptr = np.frombuffer(self._indptr, dtype=np.int32)
        indices = np.frombuffer(self._indices, dtype=np.int32)
        data = np.frombuffer(self._data, dtype=np.float64)
        
        return csr_matrix((data, indices, indptr), shape = (len(indptr) - 1, self.num_states ** 2))
    
    def states(self):
        """
        Gets the states of the created matrix in the used order.
        :return: The states as numpy ndarray
        """
        
        return self.label_encoder.classes_

if __name__ == '__main__':
    states = [ "foo", "bar", "baz" ]
    matrix = SessionMatrix(states)
     
    matrix._append_session([ "foo", "foo", "bar", "foo" ])
    matrix._append_session([ "baz", "bar" ])
    matrix._append_session([ "baz", "foo", "baz", "bar" ])
    
    csr_matrix = matrix.as_csr_matrix()
    print(csr_matrix)
    
    print(type(matrix.states()))
    print(matrix.states())
    print(csr_matrix.toarray())

