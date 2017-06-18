from collections import OrderedDict

import yaml


class VocabWord:
  def __init__(self, trad, simp, pinyin, tw_pinyin, defs, clfrs, example_sentences):
    """
    :param str trad: traditional form
    :param str simp: simplified form
    :param str pinyin: pinyin, e.g. 'nǐ hǎo' (not 'ni3 hao3')
    :param str|None tw_pinyin: Taiwanese pinyin, or None
    :param list[str] defs: list of definitions
    :param list[cedict.CedictClassifier] clfrs: list of classifiers
    :param list[ExampleSentence] example_sentences: list of example sentences
    """
    self.trad = trad
    self.simp = simp
    self.pinyin = pinyin
    self.tw_pinyin = tw_pinyin
    self.defs = defs
    self.clfrs = clfrs
    self.example_sentences = example_sentences

  def __repr__(self):
    return '{}(trad={}, simp={}, pinyin={}, tw_pinyin={}, defs={}, clfrs={}, example_sentences={})'.format(
      self.__class__.__name__,
      self.trad,
      self.simp,
      self.pinyin,
      self.tw_pinyin,
      self.defs,
      self.clfrs,
      self.example_sentences,
    )

  def to_dict(self):
    fields = ['trad', 'simp', 'pinyin', 'tw_pinyin', 'defs', 'clfrs', 'example_sentences']
    rv = []
    for field in fields:
      val = getattr(self, field)
      if not val:
        continue
      if field in ('clfrs', 'example_sentences'):
        val = [v.to_dict() for v in val]
      rv.append((field, val))

    rv = OrderedDict(rv)
    if rv['simp'] == rv['trad']:
      del rv['simp']

    return rv


class ExampleSentence:
  def __init__(self, trad, simp, pinyin, eng):
    """
    :param str trad: traditional form
    :param str simp: simplified form
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
      self.trad,
      self.simp,
      self.pinyin,
      self.eng,
    )

  def to_dict(self):
    fields = ['trad', 'simp', 'pinyin', 'eng']
    rv = OrderedDict((field, getattr(self, field)) for field in fields if getattr(self, field))
    if rv['simp'] == rv['trad']:
      del rv['simp']


# taken from https://stackoverflow.com/questions/16782112/can-pyyaml-dump-dict-items-in-non-alphabetical-order
def represent_ordereddict(dumper, data):
  value = []

  for item_key, item_value in data.items():
    node_key = dumper.represent_data(item_key)
    node_value = dumper.represent_data(item_value)

    value.append((node_key, node_value))

  return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)


yaml.add_representer(OrderedDict, represent_ordereddict)


class VocabList:
  def __init__(self, words):
    self.words = words

  def dump_to_file(self, fpath):
    data = [word.to_dict() for word in self.words]
    with open(fpath, 'w') as h:
      yaml.dump(data, h, allow_unicode=True, default_flow_style=False)
