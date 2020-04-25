"""
SUBTLEX-CH was a research project that collected subtitle files for 6243 films and analyzed the frequency of the words
in them using the ICTCLAS/NLPIR parser. This module provides an API for the wordlist produced by this study.

The files were taken from this site: http://crr.ugent.be/programs-data/subtitle-frequencies/subtlex-ch.
"""
import yaml

from cedict import Cedict


class SubtlexWord:
  TOTAL_WORDS = 33546516
  TOTAL_FILES = 6243

  def __init__(self, simp, w_count, w_cd, all_pos, all_pos_freq, rank):
    """
    :param str simp: simplified characters for word
    :param int w_count: total number of times word appeared in SUBTLEX dataset
    :param int w_cd: number of files word appeared in
    :param list[str] all_pos: all parts-of-speech
    :param all_pos_freq: number of times word appeared as each part-of-speech
    :param int rank: rank in the subtlex file (most frequent is 1, second most frequent is 2, etc.)
    """
    self.simp = simp
    self.w_count = w_count
    self.w_cd = w_cd
    self.all_pos = all_pos
    self.all_pos_freq = all_pos_freq
    self.rank = rank

  @property
  def w_million(self):
    """
    :return float: Number of times the word appeared per 1 million words in the SUBTLEX dataset
    """
    return self.w_count / self.TOTAL_WORDS * 1e6

  @property
  def w_cd_pct(self):
    """
    :return float: % of total files the word appeared in. 
    """
    return self.w_cd / self.TOTAL_FILES * 1e2

  @property
  def dominant_pos(self):
    """
    :return str: Most frequent part-of-speech
    """
    return self.all_pos[0]

  @property
  def dominant_pos_freq(self):
    """
    :return int: Number of times word appeared as dominant part-of-speech
    """
    return self.all_pos_freq[0]

  @classmethod
  def parse_from_line(cls, line, rank):
    line = line.strip()
    (simp, _, _, _, w_count, w_million, _, w_cd, w_cd_pct, _, dominant_pos, dominant_pos_freq, all_pos, all_pos_freq, *_
        ) = line.split('\t')

    w_count = int(w_count)
    w_million = float(w_million)
    w_cd = int(w_cd)
    w_cd_pct = float(w_cd_pct)
    dominant_pos_freq = float(dominant_pos_freq)
    all_pos = [piece for piece in all_pos.split('.') if piece]
    all_pos_freq = [int(piece) for piece in all_pos_freq.split('.') if piece]

    rv = SubtlexWord(
      simp=simp,
      w_count=w_count,
      w_cd=w_cd,
      all_pos=all_pos,
      all_pos_freq=all_pos_freq,
      rank=rank,
    )

    if round(rv.w_million, 2) != w_million:
      raise Exception('file is malformed, w_million value is incorrect for line {}'.format(line))

    if round(rv.w_cd_pct, 2) != w_cd_pct:
      raise Exception('file is malformed, w_cd_pct value is incorrect for line {}'.format(line))

    if rv.dominant_pos != dominant_pos:
      raise Exception('file is malformed, dominant_pos value is incorrect for line {}'.format(line))

    if rv.dominant_pos_freq != dominant_pos_freq:
      raise Exception('file is malformed, dominant_pos_freq value is incorrect for line {}'.format(line))

    return rv

  def __repr__(self):
    return '{}(simp={}, w_count={}, w_cd={}, all_pos={}, all_pos_freq={}, rank={})'.format(
      self.__class__.__name__,
      self.simp,
      self.w_count,
      self.w_cd,
      self.all_pos,
      self.all_pos_freq,
      self.rank,
    )


def load_subtlex_file(fpath):
  """
  Load SUBTLEX data as a list of SubtlexWords from the given file.

  :param str fpath: Path to file to load
  :return list[SubtlexWord]:
  """
  with open(fpath) as h:
    lines = iter(h)
    next(lines)  # skip header line

    rv = []
    for rank, line in enumerate(lines):
      rank += 1
      rv.append(SubtlexWord.parse_from_line(line, rank))

    return rv


class SubtlexList:
  @classmethod
  def load(cls):
    """
    Load SubtlexList from the file in reference_files/.

    :return SubtlexList: 
    """
    return cls(load_subtlex_file('reference_files/subtlex_ch.tsv'))

  def __init__(self, words):
    self.words = words
    self.words_by_simp = {}
    for word in words:
      if word.simp in self.words_by_simp:
        # TODO no idea why this happens
        continue
      self.words_by_simp[word.simp] = word

  def re_sort_rank_index(self):
    """
    Re-sort, re-rank, and re-index the words.
    """
    self.words.sort(key=lambda word: -word.w_count)

    for rank, word in enumerate(self.words):
      word.rank = rank + 1

    self.words_by_simp = {word.simp: word for word in self.words}


class FilteredSubtlexList(SubtlexList):
  """
  Subclass of SubtlexList that removes words that don't have CC-CEDICT entries.
  """

  @classmethod
  def load(cls):
    return cls(
      load_subtlex_file('reference_files/subtlex_ch.tsv'),
      Cedict.load())

  def __init__(self, words, cedict):
    self.words = []
    for word in words:
      if word.simp in cedict.word_lists_by_simp:
        self.words.append(word)

    self.re_sort_rank_index()


class DedupedSubtlexList(FilteredSubtlexList):
  """
  Subclass of FilteredSubtlexList that removes redundant words.
  """
  @classmethod
  def load(cls):
    return cls(
      load_subtlex_file('reference_files/subtlex_ch.tsv'),
      Cedict.load(),
      cls.load_dupes_file('contrib_files/subtlex_dupes.yaml'))

  @staticmethod
  def load_dupes_file(fpath):
    with open(fpath) as h:
      return yaml.full_load(h)

  def __init__(self, words, cedict, dupes):
    super().__init__(words, cedict)

    new_words = []
    new_words_by_simp = {}
    for word in self.words:
      # sometimes words appear twice in the file, so we de-dupe those with the previous occurrence
      if word.simp in new_words_by_simp:
        existing_word = new_words_by_simp[word.simp]
        self.combine_words(existing_word, word)
      else:
        new_words.append(word)
        new_words_by_simp[word.simp] = word
    self.words = new_words
    self.words_by_simp = new_words_by_simp

    new_words = []
    for word in self.words:
      if word.simp in dupes:
        dupe_simps = dupes[word.simp]
        if dupe_simps is None:
          continue
        if not isinstance(dupe_simps, list):
          dupe_simps = [dupe_simps]
        for dupe_simp in dupe_simps:
          if dupe_simp in self.words_by_simp:
            dupe_word = self.words_by_simp[dupe_simp]
          else:
            # for some dupes words, e.g. 干吗 -> 干嘛, the dupe word doesn't exist
            dupe_word = SubtlexWord(dupe_simp, 0, 0, [], [], -1)
            self.words.append(dupe_word)
            self.words_by_simp[dupe_simp] = dupe_word
          self.combine_words(dupe_word, word)
      else:
        new_words.append(word)
    self.words = new_words

    self.re_sort_rank_index()

  @staticmethod
  def combine_words(dest, src):
    dest.w_count += src.w_count

    dest.w_cd = max(dest.w_cd, src.w_cd)  # this is about the best we can do here :/

    # update dest.all_pos
    for i in range(len(src.all_pos)):
      for j in range(len(dest.all_pos)):
        if src.all_pos[i] == dest.all_pos[j]:
          dest.all_pos_freq[j] += src.all_pos_freq[i]
          break
      else:
        dest.all_pos.append(src.all_pos[i])
        dest.all_pos_freq.append(src.all_pos_freq[i])
    pairs = list(zip(dest.all_pos, dest.all_pos_freq))
    pairs.sort(key=lambda pair: -pair[1])
    dest.all_pos, dest.all_pos_freq = zip(*pairs)
    dest.all_pos = list(dest.all_pos)
    dest.all_pos_freq = list(dest.all_pos_freq)


class LimitedSubtlexList(DedupedSubtlexList):
  """
  Subclass of DedupedSubtlexList that limits to 10K words.
  """

  def __init__(self, words, cedict, dupes):
    super().__init__(words, cedict, dupes)
    self.words = self.words[:10000]

    self.re_sort_rank_index()
