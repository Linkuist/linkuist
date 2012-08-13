# -*- coding: utf-8 -*-
"""
    A simple lang classifer implementation using nltk

"""

import nltk
from nltk.corpus import europarl_raw

class LangClassifier(object):
    def __init__(self, langs=None):
        self.langs = langs or ('english', 'french')
        for lang in self.langs:
            corpa = getattr(europarl_raw, lang)
            attr = set(w.lower() for w in corpa.words())
            setattr(self, "%s_vocab" % lang, attr)

    def wordize(self, raw_text):
        tokens = nltk.wordpunct_tokenize(raw_text)
        text = nltk.Text(tokens)
        words = [w.lower() for w in text if w.lower().isalpha()]
        return words

    def find_language(self, raw_text):
        words = set(self.wordize(raw_text))
        min_diff = len(words)
        found_lang = None

        for lang in self.langs:
            reference = getattr(self, "%s_vocab" % lang)

            diffs = len(words.difference(reference))
            if diffs < min_diff:
                min_diff = diffs
                found_lang = lang


        return found_lang

