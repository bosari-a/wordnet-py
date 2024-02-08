import re
import os
from concurrent.futures import ThreadPoolExecutor

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


def binary_search(data: list[str], find: str, regexp: str | None = None) -> int | None:
    '''This is a basic implementation of binary search that
    has some wordnet specific details.
    This will also sort the array in place and the returned
    index will be with respect to the sorted array.
    '''
    # 1. sort data list (ascending)
    data.sort()
    # 2. while `left` index <= `right` index
    left = 0
    right = len(data)
    f = find.strip().lower()
    # wordnet words don't have '_' instead of spaces
    if " " in f:
        f = "_".join(find.split(" "))
    while left <= right:
        # find midpoint index `m` in data and compare `data[m]` with `find`
        m = (left+right)//2
        data_m = data[m]
        # in case regular expression is provided for comparison
        if regexp:
            data_m = re.search(regexp, data_m)
            if data_m:
                data_m = data_m.group()
            else:
                raise Exception("provided expression doesn't match data list")
        # 3. if `find`==`data[m]` then the value being searched for has been found, return its index: `m`
        if f == data_m:
            return m
        # 4. if `find` lies on the right side of `data[m]`, search on the right side of data
        if f > data_m:
            left = m+1
        # 5. otherwise focus search on left side
        else:
            right = m-1
    return None


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


def search_word_in_file(word: str, ext: str, dict_path: str = DEFAULT_PATH) -> dict | None:
    '''This functions searches for `word` provided in the arguments
    in the index.`ext` file where `ext` is also an argument.\n
    If a word is found the it returns a `dict` with the relevant information:
    `{"word" : word, "buffer_offsets" : list[int], "word_type" : str, "definitions" : list[str]}`.\n
    Optional argument `dict_path` defaults to `./dict`.\n
    This function also calls `get_word_meaning` which adds definitions to
    the `word["definitions"]` list if a word was found successfully.
    '''
    # 1. create path from extension and dict path
    index_file = os.path.join(dict_path, f"index.{ext}")
    found = None
    # 2. read and filter valid lines containing words in file
    with open(index_file, "r", encoding="utf-8") as fd:
        lines = [line.strip() for line in fd.readlines()
                 if re.search(WORD_REGEXP, line)]
        # 3. search for the word in the file
        i = binary_search(data=lines, find=word, regexp=WORD_REGEXP)
        # 4. if found, return a dict with the relevant information otherwise return None
        if i is not None:
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
            get_word_meaning(found, dict_path)
    return found


def search_word(word: str, dict_path: str = DEFAULT_PATH) -> list[str]:
    '''
    This function takes in a word string and sets up multiple threads which
    call `search_word_in_file` on each wordnet index file.\n
    It returns a `list[str]` which has all the definitions.
    '''
    definitions = []
    with ThreadPoolExecutor() as tp_executor:
        for ext in TYPES_EXTS.values():
            future = tp_executor.submit(
                search_word_in_file, word, ext, dict_path)
            res = future.result()
            if res:
                definitions += res.get("definitions", [])
    return definitions


def get_words_in_file(ext: str, dict_path: str = DEFAULT_PATH) -> list[str]:
    '''Parses index.`ext` file and returns a list of all the words there.
    For example, calling with `ext="noun"` will return a `list` 
    of all nouns.'''
    index_file = os.path.join(dict_path, f"index.{ext}")
    words = []
    with open(index_file, "r", encoding="utf-8") as fd:
        for line in fd.readlines():
            res = re.search(WORD_REGEXP, line)
            if res:
                words += [res.group()]
    return words


def get_words(dict_path: str = DEFAULT_PATH) -> list[str]:
    '''Creates multiple threads that parse all
    wordnet index files and returns a list
    of all the words.'''
    words = []
    with ThreadPoolExecutor() as tp_exec:
        for ext in TYPES_EXTS.values():
            future = tp_exec.submit(get_words_in_file, ext, dict_path)
            res = future.result()
            if res:
                words += res
    return words
