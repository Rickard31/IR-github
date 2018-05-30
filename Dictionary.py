import time
import chardet
import string
from deprecated import Node
import re


class Dictionary:
    def __init__(self, list_of_files):
        self.reversed_index = []
        for file_name in list_of_files:
            start = time.process_time()
            rawdata = open(file_name, "rb").read()
            encode = chardet.detect(rawdata)
            with open(file_name, "r", encoding=encode['encoding']) as file:
                for line in file.readlines():
                    for word in [w.strip(string.punctuation).lower() for w in re.split("\W+", line.rstrip())]:
                        index = self.binary_search(self, self.reversed_index, word)
                        print(word, index)
                        if not index:
                            self.insert_node(self.reversed_index, word, file_name)
                        else:
                            self.reversed_index[index].add_file(file_name)
            end = time.process_time()
            print(file_name, "done in", end - start, "s")

    def insert_node(self, array, word, file_name):
        for i in range(len(array)):
            if word < array[i].word:
                array.insert(i, Node(word, file_name))
                return
        array.append(Node(word, file_name))

    def binary_search(self, nodes_array, word):
        if (len(nodes_array) == 0):
            return False
        lower = 0
        upper = len(nodes_array)
        while lower < upper:
            x = lower + (upper - lower) // 2
            val = nodes_array[x]
            if word == val.word:
                return x
            elif word > val.word:
                if lower == x:
                    return False
                lower = x
            elif word < val.word:
                upper = x



