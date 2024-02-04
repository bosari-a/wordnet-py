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


def search_word_in_file(word: str, ext: str, dict_path: str = "./dict") -> dict | None:
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
                "word_type": TYPES_EXTS[word_type]
            }
    return found


