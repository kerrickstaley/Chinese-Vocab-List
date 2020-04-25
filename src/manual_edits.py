import subprocess
from chinesevocablist import VocabList

_MANUAL_EDIT_START = '521b4741b8e135642c131350462cfb020a3ef1f3'  # last commit before we started doing manual edits
_VOCAB_LIST_FILE = 'chinese_vocab_list.yaml'


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

    Returns a dict mapping trad to ManualEdit.
    
    If there are multiple manual edits, they will be merged, with the later one taking priority.
    """
    commits = subprocess.check_output([
        'git',
        'log',
        '--pretty=format:%H',
        '{}..HEAD'.format(_MANUAL_EDIT_START),
    ]).decode('utf8').splitlines()

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
        
        edits = _get_manual_edits_for_commit(commit)
        for edit in edits:
            if edit.trad in trad_to_edit:
                trad_to_edit[edit.trad] = trad_to_edit[edit.trad].merge(edit)
            else:
                trad_to_edit[edit.trad] = edit

        trad_to_edit.update({e.trad: e for e in edits})
    
    return trad_to_edit
