# -*- coding: utf-8 -*-
"""


"""
import pprint
import requests
import sys
import nltk
from readability.readability import Document

def extract(url):
    content = requests.get(url)
    html = content.text
    article = Document(html).summary()
    title = Document(html).short_title()
    return title, article

def main():
    """some quick mains"""
    title, article = extract("http://lxml.de/installation.html")
    raw = nltk.clean_html(article)
    tokens = nltk.word_tokenize(raw)
    print tokens
    pass

if __name__ == '__main__':
    main()
