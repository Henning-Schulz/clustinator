'''
@author: Henning Schulz
'''

import pickle
import os.path

class SessionMatrixBuffer:
    
    def __init__(self, directory, noop = False):
        self.directory = directory
        self.noop = noop
        
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def _file_path(self, app_id, tailoring, start_micros, end_micros):
        return os.path.join(self.directory, '{}-{}-{}-{}.pickle'.format(app_id, tailoring, start_micros, end_micros))
    
    def store(self, app_id, tailoring, start_micros, end_micros, session_matrix):
        """
        Stores a session matrix to a binary file, which can be loaded again based on the passed attributes.
        :param app_id: 
        :param tailoring:
        :param start_micros:
        :param end_micros: 
        :param session_matrix: The matrix to be stored. Should be a SessionMatrix object.  
        """
        if self.noop:
            return
        
        pickle.dump(session_matrix, open(self._file_path(app_id, tailoring, start_micros, end_micros), 'wb'))
    
    def load(self, app_id, tailoring, start_micros, end_micros):
        """
        Loads a session matrix from the corresponding binary file, if one exists.
        :param app_id: 
        :param tailoring:
        :param start_micros:
        :param end_micros: 
        :return: The stored SessionMatrix object or None if there is none.  
        """
        
        if self.noop:
            return None
        
        file_path = self._file_path(app_id, tailoring, start_micros, end_micros)
        
        if os.path.isfile(file_path):
            return pickle.load(open(file_path, 'rb'))
        else:
            return None
    

session_matrix_buffer_noop = SessionMatrixBuffer(None, True)
