from collections import defaultdict, OrderedDict
import re


def toned_char(c, tone):
  data = [
    ['ā', 'á', 'ǎ', 'à', 'a'],
    ['ē', 'é', 'ě', 'è', 'e'],
    ['ī', 'í', 'ǐ', 'ì', 'i'],
    ['ō', 'ó', 'ǒ', 'ò', 'o'],
    ['ū', 'ú', 'ǔ', 'ù', 'u'],
    ['ǖ', 'ǘ', 'ǚ', 'ǜ', 'ü'],
  ]
  for row in data:
    if row[4] == c:
      return row[tone - 1]


def toned_syl(syl):
  rv = []
  try:
    tone = int(syl[-1])
  except ValueError:
    return syl

  if tone == 5:
    return syl[:-1]

  curr = syl[0]
  toned = False
  for next_ in syl[1:]:
    if curr == 'u' and next_ == ':':
      curr = 'ü'
      continue
    if (curr in 'ae'
        or not toned and curr == 'o' and next_ == 'u'
        or not toned and curr in 'aeiouü' and next_ not in 'aeiouü'):
      rv.append(toned_char(curr, tone))
      toned = True
    else:
      rv.append(curr)

    curr = next_

  return ''.join(rv)


def toned_syls(syls):
  return ' '.join(toned_syl(syl) for syl in syls.split())


class CedictWord:

  LINE_REGEX = re.compile(r'(?P<trad>.+?) (?P<simp>.+?) \[(?P<pinyin>.+?)\] /(?P<defs>.+)/')

  def __init__(self, trad, simp, pinyin, tw_pinyin, defs, clfrs):
    """
    :param str trad: traditional form
    :param str simp: simplified form
    :param str pinyin: pinyin, e.g. 'nǐ hǎo' (not 'ni3 hao3')
    :param str|None tw_pinyin: Taiwanese pinyin, or None
    :param list[str] defs: list of definitions
    :param list[CedictClassifier] clfrs: list of classifiers
    """
    self.trad = trad
    self.simp = simp
    self.pinyin = pinyin
    self.tw_pinyin = tw_pinyin
    self.defs = defs
    self.clfrs = clfrs

  def __repr__(self):
    return 'CedictWord(trad={}, simp={}, pinyin={}, tw_pinyin={}, defs={}, clfrs={})'.format(
      self.trad, self.simp, self.pinyin, self.tw_pinyin, self.defs, self.clfrs)

  @classmethod
  def parse_from_line(cls, line):
    line = line.strip()
    match = cls.LINE_REGEX.match(line)

    if not match:
      raise Exception('line {} is malformatted'.format(line))

    defs = match.group('defs').split('/')

    actual_defs = []
    clfrs = None
    tw_pinyin = None
    for def_ in defs:
      if def_.startswith('CL:'):
        pieces = def_.split(':', 2)[1].split(',')
        clfrs = [CedictClassifier.parse(piece) for piece in pieces]
      elif def_.startswith('Taiwan pr. ['):
        tw_pinyin = def_.split('[')[1].rstrip(']')
      else:
        actual_defs.append(def_)

    pinyin = toned_syls(match.group('pinyin'))
    tw_pinyin = toned_syls(tw_pinyin) if tw_pinyin else None

    return cls(
      trad=match.group('trad'),
      simp=match.group('simp'),
      pinyin=pinyin,
      tw_pinyin=tw_pinyin,
      defs=actual_defs,
      clfrs=clfrs,
    )


class CedictClassifier:
  def __init__(self, trad, simp, pinyin):
    """
    :param str trad: traditional form
    :param str simp: simplified form
    :param str pinyin: pinyin, e.g. 'ge' (not 'ge5')
    """
    self.trad = trad
    self.simp = simp
    self.pinyin = pinyin

  @classmethod
  def parse(cls, s):
    if '|' in s:
      trad, rest = s.split('|')
      simp, rest = rest.split('[')
    else:
      trad, rest = s.split('[')
      simp = trad
    pinyin = rest.rstrip(']')

    return cls(trad, simp, pinyin)

  def to_dict(self):
    fields = ['trad', 'simp', 'pinyin']
    rv = OrderedDict((field, getattr(self, field)) for field in fields if getattr(self, field))

    if rv['simp'] == rv['trad']:
      del rv['simp']

    return rv


def load_cedict_file(fpath):
  """
  Load cedict from the given file as a list of CedictWords

  :param str fpath: path to file
  :return list[CedictWord]: list of words
  """
  rv = []
  with open(fpath) as h:
    for line in h:
      if line.startswith('#') or not line.strip():
        continue
      rv.append(CedictWord.parse_from_line(line))

  return rv


class Cedict:

  @classmethod
  def load(cls):
    """
    Load the dictionary from the text file stored in reference_files/.
    
    :return Cedict:
    """
    return cls(load_cedict_file('reference_files/cc_cedict.txt'))

  def __init__(self, words):
    """
    :param list[CedictWord] words: 
    """
    self.words = words
    self.word_lists_by_trad = defaultdict(list)
    self.word_lists_by_simp = defaultdict(list)
    for word in words:
      self.word_lists_by_trad[word.trad].append(word)
      self.word_lists_by_simp[word.simp].append(word)

    self.word_lists_by_trad = dict(self.word_lists_by_trad)
    self.word_lists_by_simp = dict(self.word_lists_by_simp)
