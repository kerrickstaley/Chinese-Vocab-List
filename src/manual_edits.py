import json
import os
import subprocess
import sys
from chinesevocablist import VocabList
from chinesevocablist.models import ExampleSentence

_MANUAL_EDIT_START = '521b4741b8e135642c131350462cfb020a3ef1f3'  # last commit before we started doing manual edits
_VOCAB_LIST_FILE = 'chinese_vocab_list.yaml'
_MANUAL_EDIT_CACHE_PATH = '.manual_edit_cache.json'


class ManualEdit:
    def __init__(self, trad, defs=None, example_sentences=None):
        """
        Set defs to update defs, or leave as None to use default defs. Same for example_sentences.

        Changing other fields, or adjusting rank, via manual edit is not supported.
        """
        self.trad = trad
        self.defs = defs
        self.example_sentences = example_sentences
    
    def apply_to_vocab_word(self, vocab_word):
        """
        Changes vocab_word in-place according to this ManualEdit.
        """
        if vocab_word.trad != self.trad:
            raise RuntimeError('Passed wrong VocabWord to ManualEdit.apply_to_vocab_word')
        
        if self.defs is not None:
            vocab_word.defs = self.defs
        
        if self.example_sentences is not None:
            vocab_word.example_sentences = self.example_sentences
    
    def merge(self, other):
        """
        Merges self with other. If a field is set in both self and other, will use other's version of that field.
        """
        if self.trad != other.trad:
            raise RuntimeError('Passed wrong ManualEdit to ManualEdit.merge')
        
        return ManualEdit(
            self.trad,
            defs=other.defs if other.defs is not None else self.defs,
            example_sentences=other.example_sentences if other.example_sentences is not None
                              else self.example_sentences)

    def __repr__(self):
        return '{}({}, defs={}, example_sentences={})'.format(
            self.__class__.__name__,
            self.trad,
            self.defs,
            self.example_sentences)
    
    def to_dict(self):
        example_sentences = None
        if self.example_sentences is not None:
            example_sentences = [es.to_dict() for es in self.example_sentences]
        return {
            'trad': self.trad,
            'defs': self.defs,
            'example_sentences': example_sentences,
        }
    
    @classmethod
    def from_dict(cls, d):
        example_sentences = None
        if d['example_sentences'] is not None:
            example_sentences=[ExampleSentence.from_dict(es_d) for es_d in d['example_sentences']]
        return cls(
            trad=d['trad'],
            defs=d['defs'],
            example_sentences=example_sentences)


def _get_manual_edits_for_commit(commit):
    # Note: This is slow. We could cache the result if it becomes a problem.
    before_list = VocabList.load_from_yaml_str(
        subprocess.check_output([
            'git',
            'show',
            '{}^:chinese_vocab_list.yaml'.format(commit),
        ]).decode('utf8')
    )
    after_list = VocabList.load_from_yaml_str(
        subprocess.check_output([
            'git',
            'show',
            '{}:chinese_vocab_list.yaml'.format(commit),
        ]).decode('utf8')
    )

    ret = []
    for new_word in after_list.words:
        old_word = before_list.trad_to_word[new_word.trad]
        new_defs = new_word.defs if new_word.defs != old_word.defs else None
        new_sents = new_word.example_sentences if new_word.example_sentences != old_word.example_sentences else None
        if new_defs is not None or new_sents is not None:
            ret.append(ManualEdit(new_word.trad, defs=new_defs, example_sentences=new_sents))
    
    return ret


def get_manual_edits():
    """
    Go through commit history and find all manual edits.

    Returns a list of ManualEdits.
    
    If there are multiple manual edits, they will be merged, with the later one taking priority.
    """
    commits = subprocess.check_output([
        'git',
        'log',
        '--pretty=format:%H',
        '{}..HEAD'.format(_MANUAL_EDIT_START),
    ]).decode('utf8').splitlines()

    # manual_edit_cache is a dict of commit str -> list of manual edits
    if os.path.exists(_MANUAL_EDIT_CACHE_PATH):
        with open(_MANUAL_EDIT_CACHE_PATH) as f:
            manual_edit_cache = json.load(f)
            for commit in list(manual_edit_cache.keys()):
                manual_edit_cache[commit] = [ManualEdit.from_dict(me_str) for me_str in manual_edit_cache[commit]]
    else:
        manual_edit_cache = {}

    trad_to_edit = {}
    for commit in commits:
        changed_files = subprocess.check_output([
            'git',
            'diff-tree',
            '--no-commit-id',
            '--name-only',
            '-r', commit,
        ]).decode('utf8').splitlines()
        
        if changed_files != [_VOCAB_LIST_FILE]:
            continue

        if commit not in manual_edit_cache:
            print(
                'Computing ManualEdits for commit {}. This will be slow but the result will be cached.'.format(commit),
                file=sys.stderr)
            manual_edit_cache[commit] = _get_manual_edits_for_commit(commit)

        edits = manual_edit_cache[commit]

        for edit in edits:
            if edit.trad in trad_to_edit:
                trad_to_edit[edit.trad] = trad_to_edit[edit.trad].merge(edit)
            else:
                trad_to_edit[edit.trad] = edit
    
    with open(_MANUAL_EDIT_CACHE_PATH, 'w') as f:
        for commit in list(manual_edit_cache.keys()):
            manual_edit_cache[commit] = [me.to_dict() for me in manual_edit_cache[commit]]
        json.dump(manual_edit_cache, f)

    return list(trad_to_edit.values())


def apply_manual_edits(vocab_list, manual_edits=None):
    """
    Apply manual_edits to a VocabList.

    If manual_edits is not passed, it will be computed from commit history using get_manual_edits.
    """
    if manual_edits is None:
        manual_edits = get_manual_edits()
    
    for edit in manual_edits:
        edit.apply_to_vocab_word(vocab_list.trad_to_word[edit.trad])
