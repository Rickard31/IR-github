import chardet
import time
import string
import re
import os


class Node:
    def __init__(self, char, list_of_files=None):
        self.letter = char
        self.files = list_of_files
        self.children = {}

    def __str__(self):
        return self.children


class Reversed_Tree:

    @staticmethod
    def process_word(word):
        return word.rstrip().strip(string.punctuation).lower()[::-1]

    def __add_word_to_vocabulary(self, word, file_name):
        if not word or not len(word):
            return
        if word[0] not in self.nodes.keys():
            self.nodes[word[0]] = Node(word[0])
        cur_node = self.nodes[word[0]]
        for i in range(1, len(word)):
            if word[i] not in cur_node.children.keys():
                cur_node.children[word[i]] = Node(word[i])
            cur_node = cur_node.children[word[i]]
        if not cur_node.files:
            cur_node.files = {file_name}
        else:
            cur_node.files |= {file_name}

    def is_present(self, word):
        if not word or not len(word):
            return False
        if word[0] not in self.nodes.keys():
            self.nodes[word[0]] = Node(word[0])
        cur_node = self.nodes[word[0]]
        for i in range(1, len(word)):
            if word[i] not in cur_node.children.keys():
                return False
            cur_node = cur_node.children[word[i]]
        return cur_node.files

    def __init__(self, file_folder):
        list_of_files = [f for f in os.listdir(file_folder) if os.path.isfile(os.path.join(file_folder, f))]
        self.nodes = {}
        for file_name in list_of_files:
            start = time.process_time()
            encoding = chardet.detect(open(os.path.join(file_folder, file_name), "rb").read())['encoding']
            with open(os.path.join(file_folder, file_name), "r", encoding=encoding) as file:
                words = {Reversed_Tree.process_word(w) for w in re.split("\W+", file.read().rstrip())}
                for w in words:
                    self.__add_word_to_vocabulary(w, file_name)
            end = time.process_time()
            print(file_name, "done in", end - start, "s")


if __name__ == "__main__":
    rt = Reversed_Tree("text")
    while True:
        query = input("\n\nEnter TWD search request: ")
        if query.lower() == "exit":
            break
        print(rt.is_present(Reversed_Tree.process_word(query)))
