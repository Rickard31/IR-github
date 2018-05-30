import os.path
from SPIMI import spimi_invert,  __parse_line
import lib.BitOps
from time import process_time
from lib import Token_Stream


def merge_files_compressed(blocks_directory, output_file_for_string="spimi_final_compressedString.txt",
                           output_file_for_indexes="spimi_final_comressedIndexes.txt") -> list:
    files_to_merge = [os.path.join(blocks_directory, f) for f in os.listdir(blocks_directory) if
                      os.path.isfile(os.path.join(blocks_directory, f))]
    stringLen = 0
    indexesLen = 0
    resTable = []
    with open(output_file_for_indexes, "wb") as index_output_file:
        with open(output_file_for_string, "wb") as string_output_file:
            files = [open(f, 'r', encoding='utf8') for f in files_to_merge]
            current_words = [(__parse_line(l)[0], __parse_line(l)[1]) for l in [f.readline() for f in files]]
            # print(current_words)
            while len(current_words):
                cur = current_words[0][0]
                f = []
                arr = current_words[0][1]
                for i in range(len(files)):
                    if current_words[i][0] == cur:
                        f.append(i)
                        arr = sorted(list(set(arr) | set(current_words[i][1])))  # .sort()
                    elif current_words[i][0] < cur:
                        f = [i]
                        cur = current_words[i][0]
                        arr = current_words[i][1]
                # at this stage the word is already read. Word is cur, f is list of files, where next word must be read, arr is inverted index
                c = lib.BitOps.string_to_bytes(cur)
                strIndex = stringLen
                for i in c:
                    string_output_file.write(i.to_bytes(1, 'big'))
                stringLen += len(c)

                indIndex = indexesLen
                bs = []
                for i in arr:
                    j = lib.BitOps.vb_encode(i)
                    bs.extend(j)
                for i in bs:
                    index_output_file.write(i.to_bytes(1, 'big'))
                indexesLen += len(bs)

                resTable.append((strIndex, indIndex))

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

    return resTable


if __name__ == "__main__":
    blocks_directory = 'blocks'

    for the_file in os.listdir(blocks_directory):
        file_path = os.path.join(blocks_directory, the_file)
        try:
            os.unlink(file_path)
        except Exception as e:
            print(e)

    start = process_time()
    DIRECTORY = "text"
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
    table = merge_files_compressed(blocks_directory, "text_compressedSPIMI.txt", "text_compressedIndexes.txt")
    print("Size - ",table.__sizeof__())
    end = process_time()
    print("BLOCKS MERGED IN", end - start, "s")
