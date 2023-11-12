# Chinese Vocab List
A list of Chinese vocabulary words with definitions, pronunciations, and example sentences. Under a CC-BY-SA license. See [chinese_vocab_list.yaml](https://raw.githubusercontent.com/kerrickstaley/Chinese-Vocab-List/master/chinese_vocab_list.yaml) for the list itself.

Used by the Chinese Prestudy Anki addon. See [this blog post](https://www.kerrickstaley.com/2018/09/04/chinese-prestudy) for more details.

[![Build Status](https://travis-ci.org/kerrickstaley/Chinese-Vocab-List.svg?branch=master)](https://travis-ci.org/kerrickstaley/Chinese-Vocab-List)

## Contributing
There are a few ways to contribute:
* Making changes to the source code in `src/`.
* Making changes files in `contrib_files/`:
  * `subtlex_dupes.yaml` lists words that are redundant with other words. For example, `身上: 身` in that file means that instead of learning the word "身上", someone should just learn the word "身".
  * `preferred_entries.yaml` indicates which entries from CC-CEDICT are the best to use for each word. Only needed when you increase the size of the vocab list and it complains because it finds a word with multiple definition. Note: some words have multiple meanings that are worth learning but are split across different entries in CC-CEDICT. For example, 只 and 面. I don't have a good way to represent these in `chinese_vocab_list.yaml` yet.
* Directly modifying `chinese_vocab_list.yaml`.

If you change `src/` or `contrib_files/`, be sure to run `make chinese_vocab_list.yaml` and check in both your changes and the generated changes to `chinese_vocab_list.yaml`.

## Updating reference_files:
* `cc_cedict.txt`: Run `curl https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz | gunzip > reference_files/cc_cedict.txt`
  * You may need to update contrib_files/preferred_entries.yaml and/or other files in order to handle the update. Run `make` and fix errors until the vocab list builds cleanly.

## Publishing to PyPI
If your name is Kerrick, you can publish the `chinesevocablist` package to PyPI by running these commands from the root of the repo:
```
rm -rf dist/*
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
```
Note that this directly uploads to prod PyPI and skips uploading to test PyPI.
