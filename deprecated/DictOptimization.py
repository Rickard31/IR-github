import string
import re
import time
import chardet


class Dictionary:
    def __init__(self, list_of_files):
        self.temporary_dictionary = []
        for file_name in list_of_files:
            print(file_name)
            start = time.process_time()
            rawdata = open(file_name, "rb").read()
            encode = chardet.detect(rawdata)
            with open(file_name, "r", encoding=encode['encoding']) as file:
                for line in file.readlines():
                    for word in [w.strip(string.punctuation).lower() for w in re.split("\W+", line.rstrip())]:
                        index = self.binary_search(self.temporary_dictionary, word)
                        #print(word, index, self.temporary_dictionary)
                        if not index and index!=0:
                            self.insert_node(self.temporary_dictionary, word)
            end = time.process_time()
            print(file_name, "done in", end - start, "s")


        self.reversed_index = dict.fromkeys(range(len(self.temporary_dictionary)))
        #print(self.reversed_index)

    def insert_node(self, array, word):
        for i in range(len(array)):
            if word < array[i]:
                array.insert(i, word)
                return
        array.append(word)

    def binary_search(self, nodes_array, word):
        lower = 0
        upper = len(nodes_array)
        while lower < upper:
            x = lower + (upper - lower) // 2
            val = nodes_array[x]
            if word == val:
                return x
            elif word > val:
                if lower == x:
                    return None
                lower = x
            elif word < val:
                upper = x
        return None



FILES_TO_READ = ["text/chranitel_persnya.u.txt", "text/Volodar-Persniv-Dvi-Vezhi-fb2-Dzhon-Ronald-Ruel-Tolkin.txt",
    "text/Volodar-Persniv-Povernennya-korolya-fb2-Dzhon-Ronald-Ruel-Tolkin.txt",
    "text/macbeth.txt",
    "text/king_lear.txt",
    "text/hamlet.txt", "text/julius_caesar.txt", "text/henry_v.txt",
    "text/merchant_of_venice.txt", "text/othello.txt", "text/richard_iii.txt", "text/taming_of_shrew.txt",
    "text/tempest.txt",
    "text/second_variety.txt"]

def main():
    start = time.process_time()
    TEST_FILES_TO_READ = ["test.txt", "test2.txt"]
    dict = Dictionary(FILES_TO_READ)
    print("TOOK", time.process_time()-start,"s")
    #print(dict.temporary_dictionary)


#main()
a = {}
a[1] = 1
a[1] = 2
print(a)
