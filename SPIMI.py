import os
from sys import getsizeof
from lib import Token_Stream
from time import process_time

BLOCK_SIZE = 2000000  # 10000000


def __full(dictionary, blockSize):
    return len(dictionary) > blockSize


def spimi_invert(token_stream, output_file):
    with open(output_file, "w", encoding="utf8") as output_file:
        dictionary = {}
        words_processed = 0
        while words_processed < BLOCK_SIZE:
            # while not __full(dictionary, BLOCK_SIZE):
            try:
                token, docid = token_stream.next_token()
            except StopIteration:
                print("StopIteration")
                start = process_time()
                for key in sorted(dictionary.keys()):
                    output_file.write(key + " " + str(dictionary[key]) + "\n")
                del dictionary
                end = process_time()
                print("Dictionary written in", end - start, "s")
                return True
            if token not in dictionary:
                dictionary[token] = []
            postings_list = dictionary[token]
            if not len(postings_list) or docid != postings_list[-1]:
                # if docid not in postings_list:
                postings_list.append(docid)
            words_processed += 1
        start = process_time()
        print("DICTIONARY FULL. Writing to Disk")
        for key in sorted(dictionary.keys()):
            output_file.write(key + " " + str(dictionary[key]) + "\n")
        del dictionary
        end = process_time()
        print("Dictionary written in", end - start, "s")
    print("SPIMI")
    return False


def __parse_line(line):
    if line == '':
        return None
    word, arr = line[:line.index(' ')], line[line.index(' ') + 1:].strip('[').strip(']\n')
    res_list = [int(i) for i in arr.split(',')]
    return word, res_list


def merge_files(blocks_directory, output_file="spimi_final.txt"):
    files_to_merge = [os.path.join(blocks_directory, f) for f in os.listdir(blocks_directory) if
                      os.path.isfile(os.path.join(blocks_directory, f))]
    with open(output_file, "w", encoding='utf8') as file:
        files = [open(f, 'r', encoding='utf8') for f in files_to_merge]
        current_words = [__parse_line(l) for l in [f.readline() for f in files]]
        while len(current_words):
            cur = current_words[0][0]
            f = []
            arr = current_words[0][1]
            for i in range(len(files)):
                if current_words[i][0] == cur:
                    f.append(i)
                    arr = list(set(arr) | set(current_words[i][1]))
                elif current_words[i][0] < cur:
                    f = [i]
                    cur = current_words[i][0]
                    arr = current_words[i][1]
            file.write("{} {}\n".format(cur, arr))
            to_leave = []
            for i in f:
                current_words[i] = __parse_line(files[i].readline())
            for i in range(len(current_words)):
                if current_words[i]:
                    to_leave.append(i)
                else:
                    files[i].close()
            if len(to_leave) < len(files):
                temp_files = [files[i] for i in to_leave]
                temp_words = [current_words[i] for i in to_leave]
                files = temp_files
                current_words = temp_words
    return True


if __name__ == "__main__":
    blocks_directory = 'blocks'
    for the_file in os.listdir(blocks_directory):
        file_path = os.path.join(blocks_directory, the_file)
        try:
            os.unlink(file_path)
        except Exception as e:
            print(e)

    start = process_time()
    DIRECTORY = "C:\small_db"
    token_stream = Token_Stream.Token_Stream(
        [os.path.join(DIRECTORY, f) for f in os.listdir(DIRECTORY) if os.path.isfile(os.path.join(DIRECTORY, f))])

    spimi_counter = 0
    while True:
        toCont = spimi_invert(token_stream, blocks_directory + "/block" + str(spimi_counter) + ".txt")
        spimi_counter += 1
        if toCont:
            break
    print("DONE\n\n")
    end = process_time()
    print("BLOCKS CREATED IN", end - start, "s")

    start = process_time()
    merge_files(blocks_directory, "smallDB_uncompressedSPIMI.txt")
    end = process_time()
    print("BLOCKS MERGED IN", end - start, "s")
