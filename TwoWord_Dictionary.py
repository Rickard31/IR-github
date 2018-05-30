import chardet
import time
import string
import re


class TwoWord_Dictionary:

    def __init__(self, list_of_files):
        self.__reversed_index = {}
        self.__files = list_of_files
        for file_name in list_of_files:
            start = time.process_time()
            encoding = chardet.detect(open(file_name, "rb").read())['encoding']
            with open(file_name, "r", encoding=encoding) as file:
                raw = re.split("\W+", file.read().rstrip())
                combs = []
                for i in range(1, len(raw)):
                    combs.append(
                        TwoWord_Dictionary.process_word(raw[i - 1]) + ' ' + TwoWord_Dictionary.process_word(raw[i]))
                for word in combs:
                    index = TwoWord_Dictionary.get_file_index(file_name, list_of_files)
                    if word in self.__reversed_index.keys():
                        if index not in self.__reversed_index[word]:
                            self.__reversed_index[word].add(index)
                    else:
                        self.__reversed_index[word] = {index}
                end = time.process_time()
                print(file_name, "with", len(combs) + 1, "words done in", end - start, "s")

    def search(self, request):
        raw = re.split("\W+", request.rstrip())
        combs = []
        for i in range(1, len(raw)):
            combs.append(
                TwoWord_Dictionary.process_word(raw[i - 1]) + ' ' + TwoWord_Dictionary.process_word(raw[i]))

        if not len(combs):
            return {}
        if len(combs) == 1:
            if combs[0] in self.__reversed_index.keys():
                return set(self.__files[x] for x in self.__reversed_index[combs[0]])
            return {}

        if combs[0] not in self.__reversed_index.keys():
            return {}
        res = self.__reversed_index[combs[0]]
        for i in range(1, len(combs)):
            if combs[i] not in self.__reversed_index.keys():
                return {}
            res = res & self.__reversed_index[combs[i]]
            if not len(res):
                return {}
        return set(self.__files[x] for x in res)

    @property
    def get_reversed_index(self):
        return self.__reversed_index

    @staticmethod
    def get_file_index(file_name, list_of_files):
        return list_of_files.index(file_name)

    @staticmethod
    def process_word(word):
        return word.rstrip().strip(string.punctuation).lower()


# twd = TwoWord_Dictionary(["test.txt", "test2.txt"])
twd = TwoWord_Dictionary(
    [  # "text/chranitel_persnya.u.txt", "text/Volodar-Persniv-Dvi-Vezhi-fb2-Dzhon-Ronald-Ruel-Tolkin.txt",
        # "text/Volodar-Persniv-Povernennya-korolya-fb2-Dzhon-Ronald-Ruel-Tolkin.txt",
        "text/macbeth.txt",
        "text/king_lear.txt",
        "text/hamlet.txt", "text/julius_caesar.txt", "text/henry_v.txt",
        "text/merchant_of_venice.txt", "text/othello.txt", "text/richard_iii.txt", "text/taming_of_shrew.txt",
        "text/tempest.txt",
        "text/second_variety.txt"])
print(len(twd.get_reversed_index().keys()), "unique words")

while True:
    req = input("\n\nEnter TWD search request: ")
    if req.lower() == "exit":
        break
    print(twd.search(req))
