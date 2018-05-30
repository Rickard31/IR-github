import chardet
import time
import string
import re
from lib import graph


class Coordinated_Dictionary:
    def __init__(self, list_of_files):
        self.__reversed_index = {}
        self.__files = list_of_files
        for file_name in list_of_files:
            start = time.process_time()
            encoding = chardet.detect(open(file_name, "rb").read())['encoding']
            with open(file_name, "r", encoding=encoding) as file:
                raw = re.split("\W+", file.read().rstrip())
                combs = []
                for i in range(len(raw)):
                    combs.append(Coordinated_Dictionary.process_word(raw[i]))
                counter = 0
                for word in combs:
                    index = Coordinated_Dictionary.get_file_index(file_name, list_of_files)
                    if word in self.__reversed_index.keys():
                        if index not in self.__reversed_index[word].keys():
                            self.__reversed_index[word][index] = {counter}
                        else:
                            self.__reversed_index[word][index].add(counter)
                    else:
                        self.__reversed_index[word] = {index: {counter}}
                    counter += 1
                end = time.process_time()
                print(file_name, "with", len(combs), "words done in", end - start, "s")

    def get_reversed_index(self):
        return self.__reversed_index

    def search(self, request):
        # process lexems
        start = time.process_time()
        raw = re.split("\W+", request.rstrip())
        combs = []
        for i in range(len(raw)):
            combs.append(Coordinated_Dictionary.process_word(raw[i]))

        # check for 0- and 1-words-long request
        if not len(combs):
            return []
        if len(combs) == 1:
            if combs[0] in self.__reversed_index.keys():
                return [self.__files[x] for x in self.__reversed_index[combs[0]]]
            return []
        if combs[0] not in self.__reversed_index.keys():
            return []
        res = self.__reversed_index[combs[0]].keys()
        for i in range(1, len(combs)):
            if combs[i] not in self.__reversed_index.keys():
                return []
            res = res & self.__reversed_index[combs[i]].keys()
            if not len(res):
                return []
            elif len(res)==1:
                return [self.__files[x] for x in res]


        # Build a weighted unorinted graph, in which the indexes and keywords are nodes
        sorted = {}
        for k in res:
            g = graph.Graph()
            for w in combs:
                g.add_node(w)
                for i in self.__reversed_index[w][k]:
                    g.add_node(i)
                    g.add_edge(w, i, 0)
                for i in g.nodes:
                    if isinstance(i, (int)):
                        for j in g.nodes:
                            if isinstance(j, int):
                                g.add_edge(i, j, abs(i - j))

            #calculate shortest path, between every word in every graph
            sum = 0
            for i in range(len(combs) - 1):
                sum += graph.shortest_path(g, combs[i], combs[i + 1:])
            sorted[k] = sum

        # sort by distance between keywords
        temp = list(res)
        is_sorted = False
        while not is_sorted:
            is_sorted = True
            for i in range(len(temp) - 1):
                if sorted[temp[i]] > sorted[temp[i + 1]]:
                    is_sorted = False
                    temp[i], temp[i + 1] = temp[i + 1], temp[i]

        # print(sorted)
        end = time.process_time()
        print("Search took", end - start, "s")
        return [self.__files[x] for x in temp]

    @staticmethod
    def get_file_index(file_name, list_of_files):
        return list_of_files.index(file_name)

    @staticmethod
    def process_word(word):
        return word.rstrip().strip(string.punctuation).lower()


twd = Coordinated_Dictionary(
    [  # "text/chranitel_persnya.u.txt", "text/Volodar-Persniv-Dvi-Vezhi-fb2-Dzhon-Ronald-Ruel-Tolkin.txt",
        # "text/Volodar-Persniv-Povernennya-korolya-fb2-Dzhon-Ronald-Ruel-Tolkin.txt",
        "text/macbeth.txt",
        "text/king_lear.txt",
        "text/hamlet.txt", "text/julius_caesar.txt", "text/henry_v.txt",
        "text/merchant_of_venice.txt", "text/othello.txt", "text/richard_iii.txt", "text/taming_of_shrew.txt",
        "text/tempest.txt",
        "text/second_variety.txt"])
# twd = Coordinated_Dictionary(["test.txt", "test2.txt", "test3.txt"])
print(len(twd.get_reversed_index().keys()), "unique words")
# print(twd.get_reversed_index())


while True:
    req = input("\n\nEnter TWD search request: ")
    if req.lower() == "exit":
        break
    print(twd.search(req))
