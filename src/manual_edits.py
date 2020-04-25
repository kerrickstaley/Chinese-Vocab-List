class ManualEdit:
    def __init__(trad, defs=None, example_sentences=None):
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
