# -*- coding: utf-8 -*-
"""
    Base exception at collector.

"""

class LinkExtractorException(Exception):
    pass

class FetchException(LinkExtractorException):
    pass

class ContentTypeNotFound(LinkExtractorException):
    pass

class UnsupportedContentType(LinkExtractorException):
    pass


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