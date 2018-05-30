import chardet
import time
import string
import re
import os


class TranspositionIndex:

    @staticmethod
    def process_word(word):
        return word.rstrip().strip(string.punctuation).lower()

    def __init__(self, file_folder):
        list_of_files = [os.path.join(file_folder, f) for f in os.listdir(file_folder) if
                         os.path.isfile(os.path.join(file_folder, f))]
        self.terms = {}
        self.inverted_index = {}
        for file_name in list_of_files:
            start = time.process_time()
            encoding = chardet.detect(open(file_name, "rb").read())['encoding']
            with open(file_name, "r", encoding=encoding) as file:
                for word in re.split("\W+", file.read().rstrip()):
                    w = TranspositionIndex.process_word(word)
                    if not w or not len(w):
                        continue
                    if w in self.inverted_index.keys():
                        self.inverted_index[w] |= {file_name}
                    else:
                        self.inverted_index[w] = {file_name}
                    for i in {'$' + w} | {w[i:] + '$' + w[:i] for i in range(len(w))}:
                        # for i in {w[i:] + '$' for i in range(len(w))}:
                        if i in self.terms.keys():
                            self.terms[i] |= {w}
                        else:
                            self.terms[i] = {w}
            end = time.process_time()
            print(file_name, "done in", end - start, "s")

    def joker_search(self, query):
        counter = query.count('*')
        if counter == 0:
            matching_words = set()
            for i in [self.terms[k] for k in self.terms.keys() if (query + '$' in k or '$' + query in k)]:
                matching_words |= i
            # return matching_words
            # print(matching_words)
            res = set()
            for i in matching_words:
                if i in self.inverted_index.keys():
                    res |= self.inverted_index[i]
            return res
        if counter == 1:
            q = ""
            for i in range(len(query)):
                if query[i] != '*':
                    q += query[i]
                else:
                    q = query[i + 1:].lower() + '$' + q.lower()
                    break

            matching_words = set()
            for i in [self.terms[k] for k in self.terms.keys() if k.startswith(q)]:
                matching_words |= i
            # return matching_words
            # print(matching_words)
            res = set()
            for i in matching_words:
                if i in self.inverted_index.keys():
                    res |= self.inverted_index[i]
            return res

            # self.inverted_index[i]
            # return [i for i in [self.terms[k] for k in self.terms.keys() if k.startswith(q)]]
        if counter >= 2:
            f = query.find('*')
            q1 = query[:f].lower()
            if f == -1:
                raise ValueError
            inner = []
            while True:
                f1 = query.find('*', f + 1)
                if f1 == -1:
                    q2 = query[f + 1:].lower()
                    break
                inner.append(query[f + 1:f1].lower())
                f = f1
            q = q2 + '$' + q1
            matching_words = set()
            for i in [self.terms[k] for k in self.terms.keys() if k.startswith(q)]:
                for j in i:
                    should_add = True
                    last = -1
                    for k in inner:
                        if k not in j or j.find(k, last + 2) == -1:
                            should_add = False
                            break
                        last = j.find(k, last + 2)
                    if should_add:
                        matching_words |= i
            # print(matching_words)
            res = set()
            for i in matching_words:
                if i in self.inverted_index.keys():
                    res |= self.inverted_index[i]
            return res

    # return 0


if __name__ == "__main__":
    ti = TranspositionIndex("text")
    while True:
        query = TranspositionIndex.process_word(input("\n\nEnter TWD search request: "))
        if TranspositionIndex.process_word(query) == "exit":
            break
        print(ti.joker_search(query))
