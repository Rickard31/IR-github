import os.path
import chardet
import re
import string
from math import log2, ceil
import numpy as np


class Clasterization:

    @staticmethod
    def process_word(word):
        return word.rstrip().strip(string.punctuation).lower()

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
                        w = Clasterization.process_word(t)
                        if w in local_dict:
                            local_dict[w] += 1
                        else:
                            local_dict[w] = 1
                    line = file.readline()

            self.file_length.append(tokens_amount)

            for w in local_dict.keys():
                if w in self.common_dictionary.keys():
                    self.common_dictionary[w][self.list_of_files.index(file_name)] = local_dict[w] / tokens_amount
                else:
                    self.common_dictionary[w] = {self.list_of_files.index(file_name): local_dict[w] / tokens_amount}

        self.vectors = [[] for i in range(len(self.list_of_files))]
        for word in sorted(self.common_dictionary.keys()):
            docids = set(self.common_dictionary[word].keys())
            idf = log2(len(self.list_of_files) / len(docids))
            for i in range(len(self.list_of_files)):
                if i in docids:
                    self.vectors[i].append(self.common_dictionary[word][i] * idf)
                else:
                    self.vectors[i].append(0.0)

    def __vector_len(self, index):
        square_res = 0.0
        for i in range(len(self.vectors[index])):
            square_res += self.vectors[index][i] ** 2
        return square_res ** 0.5

    def __vector_product(self, vector_a_index, vector_b_index):
        res = 0.0
        assert len(self.vectors[vector_a_index]) == len(self.vectors[vector_b_index])
        for i in range(len(self.vectors[vector_a_index])):
            res += self.vectors[vector_a_index][i] * self.vectors[vector_b_index][i]
        return res

    def cosine_similarity(self, vector_a_index, vector_b_index):
        return self.__vector_product(vector_a_index, vector_b_index) / (self.__vector_len(
            vector_a_index) * self.__vector_len(vector_b_index))

    def clasterization(self):
        l = np.random.choice(range(len(self.list_of_files)), ceil(len(self.list_of_files) ** 0.5))
        leaders = [k for k in {i for i in l}]
        res = dict()
        for docid in range(len(self.list_of_files)):
            if docid in leaders:
                continue
            id = leaders[0]
            maxSim = self.cosine_similarity(leaders[0], docid)
            for j in leaders:
                if j==id:
                    continue
                sim = self.cosine_similarity(j, docid)
                if sim > maxSim:
                    id = j
                    maxSim = sim
            res[docid] = id
        return res


if __name__ == "__main__":
    c = Clasterization("text")
    # print(c.vectors)
    print(c.clasterization())
