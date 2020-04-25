from collections import OrderedDict
import importlib
import os.path

import yaml

from .models import Classifier, ExampleSentence

from .version import __version__


class VocabWord:
  def __init__(self, trad, simp, pinyin, defs, tw_pinyin=None, clfrs=None, example_sentences=None):
    """
    :param str trad: traditional form
    :param str simp: simplified form
    :param str pinyin: pinyin, e.g. 'nǐ hǎo' (not 'ni3 hao3')
    :param list[str] defs: list of definitions
    :param str|None tw_pinyin: Taiwanese pinyin, or None
    :param list[Classifier]|None clfrs: list of classifiers
    :param list[ExampleSentence]|None example_sentences: list of example sentences
    """
    self.trad = trad
    self.simp = simp
    self.pinyin = pinyin
    self.defs = defs
    self.tw_pinyin = tw_pinyin
    self.clfrs = clfrs or []
    self.example_sentences = example_sentences or []

  def __repr__(self):
    return '{}(trad={}, simp={}, pinyin={}, defs={}, tw_pinyin={}, clfrs={}, example_sentences={})'.format(
      self.__class__.__name__,
      repr(self.trad),
      repr(self.simp),
      repr(self.pinyin),
      repr(self.defs),
      repr(self.tw_pinyin),
      repr(self.clfrs),
      repr(self.example_sentences),
    )

  def to_dict(self):
    fields = ['trad', 'simp', 'pinyin', 'defs', 'tw_pinyin', 'clfrs', 'example_sentences']
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

  @classmethod
  def from_dict(cls, d):
    if 'clfrs' in d:
      d['clfrs'] = [Classifier.from_dict(item) for item in d['clfrs']]
    if 'example_sentences' in d:
      d['example_sentences'] = [ExampleSentence.from_dict(item) for item in d['example_sentences']]

    return cls(
        trad=d['trad'],
        simp=d.get('simp', d['trad']),
        pinyin=d['pinyin'],
        defs=d['defs'],
        tw_pinyin=d.get('tw_pinyin'),
        clfrs=d.get('clfrs'),
        example_sentences=d.get('example_sentences'))

  def __eq__(self, other):
    return self.to_dict() == other.to_dict()


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
  @classmethod
  def load(cls):
    vocab_list_data = importlib.__import__(f'{__name__}.vocab_list_data', globals=globals()).vocab_list_data
    return vocab_list_data.vocab_list

  @classmethod
  def load_from_yaml_str(cls, yaml_str):
    words = [VocabWord.from_dict(d) for d in yaml.full_load(yaml_str)]
    return VocabList(words)

  @classmethod
  def load_from_yaml_file(cls, yaml_file_path):
    with open(yaml_file_path, encoding='utf-8') as h:
      words = [VocabWord.from_dict(d) for d in yaml.full_load(h)]
    return VocabList(words)

  def __init__(self, words):
    self.words = words
    self.simp_to_word = {}
    self.trad_to_word = {}
    for word in self.words:
      self.simp_to_word[word.simp] = word
      self.trad_to_word[word.trad] = word

  def dump_to_yaml_file(self, yaml_file_path):
    data = [word.to_dict() for word in self.words]
    with open(yaml_file_path, 'w') as h:
      yaml.dump(data, h, allow_unicode=True, default_flow_style=False)

  def __repr__(self):
    return 'VocabList(words={})'.format(repr(self.words))
