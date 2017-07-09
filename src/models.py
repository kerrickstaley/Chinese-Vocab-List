"""POD classes that are used by multiple files."""
from collections import OrderedDict


class Classifier:
  def __init__(self, trad, simp, pinyin):
    """
    :param str trad: traditional form
    :param str simp: simplified form
    :param str pinyin: pinyin, e.g. 'ge' (not 'ge5')
    """
    self.trad = trad
    self.simp = simp
    self.pinyin = pinyin

  def to_dict(self):
    fields = ['trad', 'simp', 'pinyin']
    rv = OrderedDict((field, getattr(self, field)) for field in fields if getattr(self, field))

    if rv['simp'] == rv['trad']:
      del rv['simp']

    return rv

  @classmethod
  def from_dict(cls, d):
    return cls(
      trad=d['trad'],
      simp=d.get('simp', d['trad']),
      pinyin=d['pinyin'],
    )

  def __repr__(self):
    return '{}(trad={}, simp={}, pinyin={})'.format(
      self.__class__.__name__,
      repr(self.trad),
      repr(self.simp),
      repr(self.pinyin),
    )


class ExampleSentence:
  def __init__(self, trad, simp, pinyin, eng):
    """
    :param str trad|None: traditional form
    :param str simp|None: simplified form
    :param str pinyin: pinyin, e.g. 'nǐ hǎo' (not 'ni3 hao3')
    :param str|None eng: English translation
    """
    self.trad = trad
    self.simp = simp
    self.pinyin = pinyin
    self.eng = eng

  def __repr__(self):
    return '{}(trad={}, simp={}, pinyin={}, eng={})'.format(
      self.__class__.__name__,
      repr(self.trad),
      repr(self.simp),
      repr(self.pinyin),
      repr(self.eng),
    )

  def to_dict(self):
    fields = ['trad', 'simp', 'pinyin', 'eng']
    rv = OrderedDict((field, getattr(self, field)) for field in fields if getattr(self, field))

    if rv.get('simp') == rv.get('trad'):
      del rv['simp']

    return rv

  @classmethod
  def from_dict(cls, d):
    return cls(
      trad=d.get('trad'),
      simp=d.get('simp'),
      pinyin=d.get('pinyin'),
      eng=d.get('eng'),
    )
