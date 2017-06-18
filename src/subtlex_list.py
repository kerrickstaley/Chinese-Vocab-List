"""
SUBTLEX-CH was a research project that collected subtitle files for 6243 films and analyzed the frequency of the words
in them using the ICTCLAS/NLPIR parser. This module provides an API for the wordlist produced by this study.

The files were taken from this site: http://crr.ugent.be/programs-data/subtitle-frequencies/subtlex-ch.
"""
from collections import defaultdict


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
    self.words_by_simp = defaultdict(list)
    for word in words:
      self.words_by_simp[word.simp].append(word)
    self.words_by_simp = dict(self.words_by_simp)
