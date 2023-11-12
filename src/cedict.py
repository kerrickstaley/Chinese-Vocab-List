from collections import defaultdict, OrderedDict
import re

import yaml

from chinesevocablist.models import Classifier


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
    :param list[Classifier] clfrs: list of classifiers
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
        clfrs = [parse_cedict_classifier(piece) for piece in pieces]
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


def parse_cedict_classifier(s):
  if '|' in s:
    trad, rest = s.split('|')
    simp, rest = rest.split('[')
  else:
    trad, rest = s.split('[')
    simp = trad
  pinyin = rest.rstrip(']')

  return Classifier(trad, simp, pinyin)


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


class CedictWithPreferredEntries(Cedict):

  REFERENCE_REGEX = re.compile('^variant of |^old variant of |^see [^ ]+\[[^\]]+\]$|^used in [^ ]+\[')

  @classmethod
  def load(cls):
    """
    :return CedictWithPreferredEntries:
    """
    return cls(load_cedict_file('reference_files/cc_cedict.txt'),
               cls.load_preferred_entries_file('contrib_files/preferred_entries.yaml'))

  @staticmethod
  def load_preferred_entries_file(fpath):
    with open(fpath) as h:
      return yaml.full_load(h)

  def pick_entry(self, simp=None, trad=None):
    if bool(simp) == bool(trad):
      raise Exception('must pass exactly one of simp and trad')

    if simp:
      options = self.word_lists_by_simp[simp]
    else:
      options = self.word_lists_by_trad[trad]

    options = [opt for opt in options if not self.is_reference_entry(opt)]

    if len(options) == 1:
      return options[0]

    if simp and simp in self.preferred_entries:
      preferred = self.preferred_entries[simp]
      valid_options = []
      for option in options:
        if 'trad' in preferred and option.trad != preferred['trad']:
          continue
        # TODO this is sorta messy, we should be consistent about whether we store in ASCII format or not
        if 'pinyin' in preferred and option.pinyin != toned_syls(preferred['pinyin']):
          continue
        valid_options.append(option)
      if len(valid_options) != 1:
        raise Exception('{} had a preferred entry, but there are {} valid options: {}'.format(
          simp, len(valid_options), valid_options))

      return valid_options[0]

    # one last heuristic: try removing all the entries whose pinyin starts with a capital letter and see if there is
    # only one entry left. This filters out things like "能: surname Neng"
    options_filtered = [opt for opt in options if not ('A' <= opt.pinyin[0] <= 'Z')]
    if len(options_filtered) == 1:
      return options_filtered[0]

    return None

  @classmethod
  def is_reference_entry(cls, entry):
    """
    Check if `entry` is just a reference to another entry (we should never include it if this is the case)
    :param CedictWord entry:
    :return bool:
    """
    return cls.REFERENCE_REGEX.match(entry.defs[0])

  def __init__(self, words, preferred_entries):
    super().__init__(words)
    self.preferred_entries = preferred_entries
    self.words_by_trad = {t: self.pick_entry(trad=t) for t in self.word_lists_by_trad}
    self.words_by_simp = {s: self.pick_entry(simp=s) for s in self.word_lists_by_simp}
