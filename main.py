from pprint import pprint
import re
import os
from concurrent.futures import ThreadPoolExecutor
import bsearch

WORD_REGEXP = r'^[\w.-]+\b'
'''regular expression for matching words'''
BUFFER_OFF = re.compile(r'\d{8}')
'''regular expression for matching buffer offsets in index files'''
WORD_TYPE = re.compile(r'\b[a-z]\b')
'''regular expression for matching word type in index files (adj,noun,verb,adverb)'''
TYPES_EXTS = {
    "n": "noun",
    "r": "adv",
    "v": "verb",
    "a": "adj"
}
'''This dictionary specifies the wordnet file extensions
and the corresponding word type labels found in index files'''
DEFAULT_PATH = "./dict"
'''This is the default path to the wordnet database.'''


def search_word_in_index(word: str, ext: str, dict_path: str = DEFAULT_PATH) -> dict | None:
    '''This functions searches for `word` provided in the arguments
    in the index.`ext` file where `ext` is also an argument.\n
    If a word is found the it returns a `dict` with the relevant information:
    `{"word" : word, "buffer_offsets" : list[int], "word_type" : str}`.\n
         Optional argument `dict_path` defaults to `./dict`.
    '''
    # 1. create path from extension and dict path
    index_file = os.path.join(dict_path, f"index.{ext}")
    found = None
    # 2. read and filter valid lines containing words in file
    with open(index_file, "r", encoding="utf-8") as fd:
        lines = [line.strip() for line in fd.readlines()
                 if re.search(WORD_REGEXP, line)]
        # 3. search for the word in the file
        i = bsearch.binary_search(data=lines, find=word, regexp=WORD_REGEXP)
        # 4. if found, return a dict with the relevant information otherwise return None
        if i:
            line = lines[i]
            word_type_match = WORD_TYPE.search(line)
            word_type = ""
            if word_type_match:
                word_type = word_type_match.group()
            found = {
                "word": word.strip().lower(),
                "buffer_offsets": [int(off) for off in BUFFER_OFF.findall(line)],
                "word_type": word_type
            }
    return found


def get_word_meaning(word: dict, dict_path: str = DEFAULT_PATH):
    '''This function mutates the `word` dict by
    adding `definitions` key whose value is different
    definitions of the word (if found).'''
    data_path = os.path.join(
        dict_path, f"data.{TYPES_EXTS[word['word_type']]}")
    with open(data_path, "r", encoding="utf-8") as fd:
        buffer_offsets = word.get("buffer_offsets", [])
        for offset, num in zip(buffer_offsets, range(1, len(buffer_offsets)+1)):
            fd.seek(offset, 0)
            definition = "".join(fd.readline().split("|")[-1]).strip()
            word["definitions"] = word.get(
                "definitions", [])+[f"({TYPES_EXTS[word['word_type']]} {num}) {definition}"]


def get_all_meanings(word: str, dict_path: str = DEFAULT_PATH):
    '''
    This function takes in a word string and sets up multiple threads which
    call `search_word_in_index` on each wordnet index file and uses
    the resulting `word_type` and `buffer_offsets` from each thread to
    parse the data files and get the word definitions for each word type.
    '''
    return