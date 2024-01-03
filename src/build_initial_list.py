import sys

from chinesevocablist import VocabWord, VocabList
from cedict import CedictWithPreferredEntries
from example_sentences_list import ExampleSentenceList
from hsk_list import HSKList
from subtlex_list import LimitedSubtlexList
from manual_edits import apply_manual_edits

HSK_WEIGHT = 1
SUBTLEX_WEIGHT = 1
# for a given level, this gives the mean rank of a word in that level
HSK_LEVEL_TO_RANK = {
  1: 150 / 2,
  2: 150 + 150 / 2,
  3: 300 + 300 / 2,
  4: 600 + 600 / 2,
  5: 1200 + 1300 / 2,
  6: 2500 + 2500 / 2,
}
NUM_WORDS_TO_GENERATE = 4500


def combine_hsk_subtlex_ranks(hsk_rank, subtlex_rank):
  # assuming Zipf's law, so we take a (weighted) harmonic mean
  denominator = HSK_WEIGHT / hsk_rank + SUBTLEX_WEIGHT / subtlex_rank
  if denominator == 0:
    return float('inf')
  return (HSK_WEIGHT + SUBTLEX_WEIGHT) / denominator


def main():
  hl = HSKList.load()
  sl = LimitedSubtlexList.load()
  cd = CedictWithPreferredEntries.load()
  all_simp = {w.simp for w in hl.words + sl.words}
  all_simp_rank = []
  for simp in sorted(all_simp):
    if simp in hl.word_lists_by_simp:
      hsk_level = min(word.level for word in hl.word_lists_by_simp[simp])
      hsk_rank = HSK_LEVEL_TO_RANK[hsk_level]
    else:
      hsk_rank = float('inf')

    if simp in sl.words_by_simp:
      subtlex_rank = sl.words_by_simp[simp].rank
    else:
      subtlex_rank = float('inf')

    all_simp_rank.append((simp, combine_hsk_subtlex_ranks(hsk_rank, subtlex_rank)))

  all_simp_rank.sort(key=lambda pair: pair[1])

  vocab_words = []
  for simp, _ in all_simp_rank[:NUM_WORDS_TO_GENERATE]:
    try:
      entry = cd.words_by_simp[simp]
    except KeyError:
      continue  # TODO port over extra defs logic
    if entry is None:
      raise Exception('no unique entry for {}, options are:\n{}'.format(simp, '\n'.join('- ' + repr(i) for i in cd.word_lists_by_simp[simp])))
    vw = VocabWord(
      trad=entry.trad,
      simp=simp,
      pinyin=entry.pinyin,
      tw_pinyin=entry.tw_pinyin,
      defs=entry.defs,
      clfrs=entry.clfrs,
      example_sentences=[])
    vocab_words.append(vw)
  vocab_list = VocabList(vocab_words)

  example_sentence_list = ExampleSentenceList.load()
  set_example_sentences(vocab_list, example_sentence_list)

  apply_manual_edits(vocab_list)

  vocab_list.dump_to_yaml_file('/dev/stdout')


def set_example_sentences(vocab_list, example_sentences_list):
  for vocab_word in vocab_list.words:
    if vocab_word.simp in example_sentences_list.simp_to_sents:
      vocab_word.example_sentences = [
        example_sentences_list.simp_to_sents[vocab_word.simp][0]
      ]


if __name__ == '__main__' and not hasattr(sys, 'ps1'):
  main()
