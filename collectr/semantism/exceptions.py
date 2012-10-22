# -*- coding: utf-8 -*-
"""
    Base exception at collector.

"""


class BaseIndexException(Exception):
    pass

class DeleteLinkException(BaseIndexException):
    pass

class UnsupportedContentException(BaseIndexException):
    pass

class UrlExtractException(BaseIndexException):
    pass

class UrlCreationException(BaseIndexException):
    pass