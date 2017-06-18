class HSKWord:
  def __init__(self, simp, pos, level):
    """
    :param str simp: simplified characters
    :param str|None pos: part-of-speech, e.g. '介词'
    :param int level: HSK level
    """
    self.simp = simp
    self.pos = pos
    self.level = level

  def __repr__(self):
    return '{}(simp={}, pos={}, level={})'.format(
      self.__class__.__name__,
      self.simp,
      self.pos,
      self.level,
    )

  @classmethod
  def parse_from_line(cls, line):
    line = line.strip()
    simp, pos, level = line.split(',')
    if not pos:
      pos = None
    level = int(level)
    return cls(
      simp=simp,
      pos=pos,
      level=level,
    )


def load_hsk_file(fpath):
  """
  Load HSK wordlist as a list of HSKWords from file.

  :param str fpath: path to file
  :return list[HSKWord]: 
  """
  rv = []
  with open(fpath) as h:
    for line in h:
      rv.append(HSKWord.parse_from_line(line))

  return rv


class HSKList:
  @classmethod
  def load(cls):
    """
    Load HSKList from the file in reference_files/

    :return HSKList: 
    """
    return cls(load_hsk_file('reference_files/hsk_wordlist.csv'))

  def __init__(self, words):
    """
    :param list[HSKWord] words: 
    """
    self.words = words
    self.words_by_simp = {}
    for word in words:
      self.words_by_simp[word.simp] = word
