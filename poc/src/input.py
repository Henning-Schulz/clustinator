import re


class Input:

    def __init__(self, sessions_file):
        self.sessions_file = sessions_file

    def sessions(self, slice_from, slice_to):
        """
        In this function the raw session data is load in. Beside from the whole session data can be slice out dataframe.
        :param slice_from: start slice from - int
        :param slice_to: end slice to - int
        :return: The whole dataframe or sliced dataframe.
        """
        s_r_dict = {}
        # Dict of sessions
        with open(self.sessions_file) as fn:
            sessions_raw = fn.readlines()

        for session in sessions_raw:
            key = re.search('([^.]+)', session).group()
            value = re.findall('\"(.*?)\"', session)
            s_r_dict[key] = value
        if slice_from == None and slice_to == None:
            return s_r_dict
        else:
            slice_session = {k: s_r_dict[k] for k in list(s_r_dict)[slice_from:slice_to]}
            return slice_session
