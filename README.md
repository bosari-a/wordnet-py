# Wordnet-py

Simple WordNet API in Python3.

## Description

This is a WordNet API written in Python3 that utilizes multithreading and binary search to list and search for words in the English language. It exports two main functions, one for listing words in the English language as provided by the WordNet database and one that returns the different (adj,verb,noun,adv) definitions of a particular word if it is available in the database.

## Install

coming soon!

## Usage

### `search_word`

```py
search_word(word: str, dict_path: str = DEFAULT_PATH) -> list[str]
```

This function takes the `word` you want to search for as an argument and `dict_path` (which defaults to `"./dict"`) and returns a list of definitions for that word. The path `".dict/"` is the path to the wordnet files:

- index.noun
- data.noun
- index.verb
- data.verb
- index.adj
- data.adj
- index.adv
- data.adv

These can be installed, follow the [guide below.](#download-wordnet-files)

### `get_words`

```py
get_words(dict_path: str = DEFAULT_PATH)
```

This function also takes optional parameter `dict_path` and returns a list containing all of the words in the database.

## Download WordNet files

### linux

- Database files: [WNdb-3.0.tar.gz](https://wordnetcode.princeton.edu/3.0/WNdb-3.0.tar.gz)
- [What command do I need to unzip/extract a .tar.gz file?](https://askubuntu.com/a/25348)

### windows

- Download the [WordNet browser, command-line tool, and database files with InstallShield self-extracting installer](https://wordnetcode.princeton.edu/2.1/WordNet-2.1.exe)

- Follow the installation process and make sure you remember the folder where you installed `WordNet`.

- Go to the `dict` folder and copy the highlighted files (below) into a database folder (e.g. name it `dict`) in your project:
  ![screenshot of highlighted files](https://raw.githubusercontent.com/bosari-a/wordnet-parser/main/assets/windowswordnet.png)

## License

- [WordNet License](https://wordnet.princeton.edu/license-and-commercial-use)
