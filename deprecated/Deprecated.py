import pickle
import time
import string
import re
import chardet
import sys
import os
import bisect

FILES_TO_READ = [#"text/chranitel_persnya.u.txt", "text/Volodar-Persniv-Dvi-Vezhi-fb2-Dzhon-Ronald-Ruel-Tolkin.txt",
    #"text/Volodar-Persniv-Povernennya-korolya-fb2-Dzhon-Ronald-Ruel-Tolkin.txt",
    "text/macbeth.txt",
    "text/king_lear.txt",
    "text/hamlet.txt", "text/julius_caesar.txt", "text/henry_v.txt",
    "text/merchant_of_venice.txt", "text/othello.txt", "text/richard_iii.txt", "text/taming_of_shrew.txt",
    "text/tempest.txt",
    "text/second_variety.txt"]
TEST_FILES_TO_READ = ["test.txt", "test2.txt"]


class Node:
    word = None
    files = None

    def __init__(self, word, file):
        self.word = word
        self.files = {file}
        # print(self.files)

    def add_file(self, file_name):
        self.files |= {file_name}

    def __str__(self):
        # print(self.files)
        return self.word + " : " + str(self.files)

    def __lt__(self, other):
        return self.word < other.word

    def __gt__(self, other):
        return self.word > other.word

    def __eq__(self, other):
        return self.word == other.word


def read_files_to_reverse_index(files):
    reversed_index = []
    for file_name in files:
        start = time.process_time()
        rawdata = open(file_name, "rb").read()
        encode = chardet.detect(rawdata)
        file = open(file_name, "r", encoding=encode['encoding'])
        for line in file.readlines():
            for word in [w.strip(string.punctuation).lower() for w in re.split("\W+", line.rstrip())]:
                index = binary_search(reversed_index, word)
                #print(word, index)
                if index==None:
                    insert_node(reversed_index, word, file_name)
                else:
                    reversed_index[index].add_file(file_name)

        file.close()
        end = time.process_time()
        print(file_name, "done in", end - start, "s")
    return reversed_index


def binary_search(nodes_array, word):
    lower = 0
    upper = len(nodes_array)
    while lower < upper:
        x = lower + (upper - lower) // 2
        val = nodes_array[x]
        if word == val.word:
            return x
        elif word > val.word:
            if lower == x:
                return None
            lower = x
        elif word < val.word:
            upper = x


def insert_node(array, word, file_name):
    for i in range(len(array)):
        if word < array[i].word:
            array.insert(i, Node(word, file_name))
            return
    array.append(Node(word, file_name))


def read_files_to_array_vocabulary(files_to_read, vocabulary):
    for file in files_to_read:
        __read_file_to_array_vocabulary(file, vocabulary)


def __read_file_to_array_vocabulary(file_name, vocabulary):
    start = time.process_time()
    rawdata = open(file_name, "rb").read()
    encode = chardet.detect(rawdata)
    # print(encode)
    file = open(file_name, "r", encoding=encode['encoding'])
    # file_size = 0
    for line in file.readlines():
        for word in [w.strip(string.punctuation).lower() for w in re.split("\W+", line.rstrip())]:
            if word not in vocabulary:
                vocabulary.append(word)
            # file_size += 1
            # add_word_to_vocabulary(word.lower(), file_name, reversed_index)
    file.close()
    # collection_size[file_name] = file_size
    end = time.process_time()
    print(file_name + " done in ", end - start, "s")
    return vocabulary


def read_files_to_incident_matrix(files):
    vocabulary = []
    matrix = []
    for file_name in files:
        start = time.process_time()
        rawdata = open(file_name, "rb").read()
        encode = chardet.detect(rawdata)
        file = open(file_name, "r", encoding=encode['encoding'])
        for line in file.readlines():
            for word in [w.strip(string.punctuation).lower() for w in re.split("\W+", line.rstrip())]:
                try:
                    index = vocabulary.index(word)
                    matrix[index][files.index(file_name)] = True
                except ValueError:
                    # print("ValueError")
                    vocabulary.append(word)
                    matrix.append([False for x in range(len(files))])
                    index = len(vocabulary) - 1
                    matrix[index][files.index(file_name)] = True
        file.close()
        end = time.process_time()
        print(file_name + " done in ", end - start, "s")
    return vocabulary, matrix


def dump_into_file(obj, file_name):
    start = time.process_time()
    file = open(file_name, "wb")
    pickle.dump(obj, file)
    file.close()
    end = time.process_time()
    print("Dumped in", end - start, "s")


def bool_search(request, reversed_index, files):
    cur = '.and'
    res = set()
    or_set = set()
    words = request.split()
    # print(words)

    if words[0] != '.or' and words[0] != '.not' and words[0] != '.and':
        index = binary_search(reversed_index, words[0].strip(string.punctuation).lower())
        if not index:
            print("Empty returned")
            return set()
        res = reversed_index[index].files
    else:
        res = set(files)
        cur = words[0]

    for i in range(1, len(words)):
        if words[i] == '.and' or words[i] == '.not' or words[i] == '.or':
            if cur == 'or':
                print(or_set)
                temp = set()
                for word in or_set:
                    index = binary_search(reversed_index, word)
                    if not index:
                        continue
                    for file in reversed_index[index].files:
                        temp.add(file)
                res = temp
            cur = words[i]
        else:
            if cur == '.or':
                or_set |= {words[i].strip(string.punctuation).lower()}
            elif cur == '.and':
                index = binary_search(reversed_index, words[i].strip(string.punctuation).lower())
                if not index:
                    print("Empty returned")
                    return set()
                to_leave = reversed_index[index].files
                temp = set()
                for j in res:
                    if j in to_leave:
                        temp.add(j)
                res = temp
            elif cur == '.not':
                index = binary_search(reversed_index, words[i].strip(string.punctuation).lower())
                if index:
                    to_remove = reversed_index[index].files
                    temp = set()
                    for j in res:
                        if j not in to_remove:
                            temp.add(j)
                    res = temp
            else:
                "Command, but not a command"
        # print(res)
        if len(res) == 0:
            return res

    if cur == '.or':
        print(or_set)
        temp = set()
        for word in or_set:
            index = binary_search(reversed_index, word)
            if not index:
                continue
            for file in reversed_index[index].files:
                temp.add(file)
        res = temp
    return res


def main():
    start = time.process_time()
    reversed_index = read_files_to_reverse_index(FILES_TO_READ)


    end = time.process_time()
    print("REVERSED DONE IN", end - start, "s\n\n")

    start = time.process_time()
    # incident = read_files_to_incident_matrix(FILES_TO_READ)
    end = time.process_time()
    print("INCIDENT DONE IN", end - start, "s\n\n")

    # dump_into_file(incident[0], "cache_vocabulary.txt")
    # dump_into_file(incident[1], "cache_matrix.txt")
    dump_into_file(reversed_index, "cache_reversed.txt")

    #reversed_index = pickle.load(open('cache_reversed.txt', 'rb'))

    while True:
        req = input("\n\nEnter bool search request: ")
        if req == "exit":
            break
        print(bool_search(req, reversed_index, FILES_TO_READ))


main()


def search(self, request):
    raw = re.split("\W+", request.rstrip())
    combs = []
    for i in range(len(raw)):
        combs.append(Coordinated_Dictionary.process_word(raw[i]))

    if not len(combs):
        return {}
    if len(combs) == 1:
        if combs[0] in self.__reversed_index.keys():
            return set(self.__files[x] for x in self.__reversed_index[combs[0]])
        return {}

    if combs[0] not in self.__reversed_index.keys():
        return {}
    res = self.__reversed_index[combs[0]].keys()
    for i in range(1, len(combs)):
        if combs[i] not in self.__reversed_index.keys():
            return {}
        res = res & self.__reversed_index[combs[i]].keys()
        if not len(res):
            return {}

    sorted = {}
    for k in res:
        graph = {}
        for w in combs:
            indexes = self.__reversed_index[w][k]
            temp = dict()
            for i in indexes:
                temp[i] = 1
            graph[w] = temp
        # print(graph)

        graph_final = {}
        for keyI in graph.keys():
            for keyJ in graph.keys():
                if keyI == keyJ:
                    continue
                for ii in graph[keyI].keys():
                    for jj in graph[keyJ].keys():
                        """
                        if jj < ii:
                            if jj in graph_final.keys():
                                graph_final[jj][ii] = ii - jj
                            else:
                                graph_final[jj] = {ii: ii - jj}
                        else:
                            if ii in graph_final.keys():
                                graph_final[ii][jj] = jj - ii
                            else:
                                graph_final[ii] = {jj: jj - ii}
                        """
                        d = abs(ii - jj)
                        if jj in graph_final.keys():
                            graph_final[jj][ii] = d
                        else:
                            graph_final[jj] = {ii: d}
                        if ii in graph_final.keys():
                            graph_final[ii][jj] = d
                        else:
                            graph_final[ii] = {jj: d}
        print(graph)
        graph_final.update(graph)
        print(graph_final)

        distance = 0
        for i in range(len(combs)):
            for j in range(i + 1, len(combs)):
                distance += ShortestPath.shortestPath(graph_final, combs[i], combs[j])
        sorted[k] = distance

    print(sorted)
    return res