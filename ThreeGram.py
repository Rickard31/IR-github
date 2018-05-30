import chardet
import time
import string
import re
import os


class ThreeGram:

    @staticmethod
    def process_word(word):
        return word.rstrip().strip(string.punctuation).lower()

    @staticmethod
    def get_threegrams(word):
        w = ThreeGram.process_word(word)
        if not w or not len(w) or len(w) == 1:
            return None
        if len(w) == 2:
            return {'$' + w} | {w + '$'}
        res = {'$' + w[:2]} | {w[len(w) - 2:] + '$'}
        for i in range(len(w) - 2):
            res |= {w[i:i + 3]}
        return res

    def __init__(self, file_folder):
        list_of_files = [os.path.join(file_folder, f) for f in os.listdir(file_folder) if
                         os.path.isfile(os.path.join(file_folder, f))]
        self.threegrams = {}
        self.inverted_index = {}
        for file_name in list_of_files:
            start = time.process_time()
            encoding = chardet.detect(open(file_name, "rb").read())['encoding']
            with open(file_name, "r", encoding=encoding) as file:
                for w in re.split("\W+", file.read().rstrip()):
                    g = ThreeGram.get_threegrams(w)
                    word = ThreeGram.process_word(w)
                    if not g:
                        continue
                    if word:
                        if word in self.inverted_index.keys():
                            self.inverted_index[word] |= {file_name}
                        else:
                            self.inverted_index[word] = {file_name}
                    for i in g:
                        if i in self.threegrams.keys():
                            self.threegrams[i] |= {word}
                        else:
                            self.threegrams[i] = {word}
            end = time.process_time()
            print(file_name, "done in", end - start, "s")
        print(self.threegrams)


if __name__ == "__main__":
    tg = ThreeGram("text")
