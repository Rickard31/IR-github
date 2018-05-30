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