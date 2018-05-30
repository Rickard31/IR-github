import os.path
import chardet
import re
import string
from math import log2


class Ranger:

    @staticmethod
    def process_word(word):
        return word.rstrip().strip(string.punctuation).lower()

    @staticmethod
    def __process_zone(zone_text):
        tokens = re.split("\W+", zone_text.rstrip())
        tf_index = dict()
        for token in tokens:
            word = Ranger.process_word(token)
            if word in tf_index.keys():
                tf_index[word] += 1
            else:
                tf_index[word] = 1
        for key in tf_index:
            tf_index[key] /= len(tokens)
        return tf_index

    def __init__(self, text_directory):
        self.list_of_files = [os.path.join(text_directory, f) for f in os.listdir(text_directory) if
                              os.path.isfile(os.path.join(text_directory, f))]
        self.common_dictionary = dict()
        self.file_length = []
        for file_name in self.list_of_files:
            print(file_name)
            encoding = chardet.detect(open(file_name, "rb").read())['encoding']
            local_dict = {}
            tokens_amount = 0
            with open(file_name, "r", encoding=encoding) as file:
                line = file.readline()
                while line and len(line):
                    tokens = re.split("\W+", line.rstrip())
                    tokens_amount += len(tokens)
                    for t in tokens:
                        w = Ranger.process_word(t)
                        if w in local_dict:
                            local_dict[w] += 1
                        else:
                            local_dict[w] = 1
                    line = file.readline()

            self.file_length.append(tokens_amount)

            for w in local_dict.keys():
                if w in self.common_dictionary.keys():
                    self.common_dictionary[w][self.list_of_files.index(file_name)] = {
                        'body': local_dict[w] / tokens_amount}
                else:
                    self.common_dictionary[w] = {
                        self.list_of_files.index(file_name): {'body': local_dict[w] / tokens_amount}}

            tf_title = Ranger.__process_zone(file_name.split("\\")[-1].strip(".txt"))
            for w in tf_title:
                if w in self.common_dictionary.keys():
                    if self.list_of_files.index(file_name) in self.common_dictionary.keys():
                        self.common_dictionary[w][self.list_of_files.index(file_name)]['title'] = tf_title[w]
                    else:
                        self.common_dictionary[w][self.list_of_files.index(file_name)] = {'title': tf_title[w]}
                else:
                    self.common_dictionary[w] = {self.list_of_files.index(file_name): {'title': tf_title[w]}}

    ZONE_WEIGHTS = {'title': 0.95, 'body': 0.05}

    def zone_search(self, query):
        scores = [0.0 for i in range(len(self.list_of_files))]

        query_tokens = [Ranger.process_word(t) for t in re.split("\W+", query.rstrip())]
        weights_term_query = [1.0 for i in range(len(query_tokens))]

        for token_index in range(len(query_tokens)):
            token = query_tokens[token_index]
            if token not in self.common_dictionary.keys():
                continue
            posting_td = self.common_dictionary[token]

            idf = log2(len(self.list_of_files) / len(posting_td))
            for docid in posting_td.keys():
                for zone_name in self.ZONE_WEIGHTS.keys():
                    if zone_name in posting_td[docid].keys():
                        scores[docid] += posting_td[docid][zone_name] * self.ZONE_WEIGHTS[zone_name] * idf * \
                                         weights_term_query[token_index]

        for i in range(len(scores)):
            scores[i] /= self.file_length[i]

        AMOUNT_OF_RESULTS_TO_RETURN = 5
        res = []
        for i in range(AMOUNT_OF_RESULTS_TO_RETURN):
            j = scores.index(max(scores))
            if scores[j] <= 0:
                break
            res.append(self.list_of_files[j])
            scores[j] = -1

        return res


if __name__ == "__main__":
    ranger = Ranger("text")
    while True:
        req = input("\n\nEnter Ranger search request: ")
        if req.lower() == "exit":
            break
        print(ranger.zone_search(req))
