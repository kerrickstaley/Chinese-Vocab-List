import re

from models import ExampleSentence


def load_spoonfed_example_sentences_file(fpath):
  """
  Load data from Timo's Spoonfed Chinese example sentences TSV file.

  N.B. This file only contains simplified examples :( So the .trad property on each returned value will be None.

  :param str fpath: path to file
  :return list[ExampleSentence]:
  """
  rv = []
  br_re = re.compile(' ?<br ?/> ?')

  with open(fpath) as h:
    for line in h:
      eng, pinyin, simp = line.strip().split('\t')

      eng = br_re.sub('\n', eng).strip()
      pinyin = br_re.sub('\n', pinyin).strip()
      simp = br_re.sub('\n', simp).strip()

      pinyin = pinyin.lower()

      rv.append(ExampleSentence(None, simp, pinyin, eng))

  return rv


class ExampleSentenceList:
  @classmethod
  def load(cls):
    return cls(load_spoonfed_example_sentences_file('reference_files/spoonfed_sentences.tsv'))

  def __init__(self, sents):
    self.sents = sents
    self.trad_to_sents = {}
    self.simp_to_sents = {}
    for sent in self.sents:
      if sent.trad:
        self._add_sent_to_dict(sent, sent.trad, self.trad_to_sents)
      if sent.simp:
        self._add_sent_to_dict(sent, sent.simp, self.simp_to_sents)

  @staticmethod
  def _add_sent_to_dict(sent, chars, dict_):
    """
    :param ExampleSentence sent:
    :param str chars: Either sent.trad or sent.simp.
    :param dict dict_:
    """
    max_word_length = 4
    processed_words = {''}
    for start in range(len(chars)):
      for end in range(start + 1, start + 1 + max_word_length):
        word = chars[start:end]
        if word in processed_words:
          continue
        processed_words.add(word)
        dict_.setdefault(word, [])
        dict_[word].append(sent)

