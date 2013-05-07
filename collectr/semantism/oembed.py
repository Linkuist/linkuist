import json
import logging
import re
import requests


PROVIDERS = {
    'imgur': {
        'url': 'http://api.imgur.com/oembed',
        'regex': [".*imgur.com\/.*"],
        'maxwidth': 800,
    },
    'youtube': {
        'url': 'http://www.youtube.com/oembed',
        'regex': [".*youtube.*\watch\?v\=.*"],
        'maxwidth': 400,
    },
    'vimeo': {
        'url': 'http://vimeo.com/api/oembed.json',
        'regex': ['^http:\/\/.vimeo\.com\/\d+',
                  'http:\/\/www\.vimeo\.com\/groups\/.*\/videos\/.*',
                  'http:\/\/www\.vimeo\.com\/.*',
                  'http:\/\/vimeo\.com\/groups\/.*\/videos\/.*',
                  'http:\/\/vimeo\.com\/.*'],
        'maxwidth': 400,
    },
    'flickr': {
        'url': 'http://flickr.com/services/oembed',
        'regex': ['http://(?:www\.)?flickr\.com/photos/\S+?/(?:sets/)?\d+/?'],
        'maxwidth': 1200,
        'maxheight': 1200,

    },
    'instagram': {
        'url': 'http://api.instagram.com/oembed',
        'regex': ['^http:\/\/instagr.am\/p\/.*',
                  '^http:\/\/instagram\.com\/p\/.*'],
        'maxwidth': 400,
    },
    'dailymotion': {
        'url': 'http://www.dailymotion.com/services/oembed',
        'regex': ['.*.www\.dailymotion\.com\/video\/.*'],
        'maxwidth': 400,
    },
    'soundcloud': {
        'url': 'http://soundcloud.com/oembed',
        'regex': ['^.*:\/\/soundcloud.com/.*/.*'],
        'maxwidth': 400,
    },
}


logger = logging.getLogger(__name__)


class OEmbedResolutionException(Exception):
    pass


def get_provider(url):
    for provider_name, infos in PROVIDERS.items():
        for regex in infos['regex']:
            if re.match(regex, url):
                return infos
    return None


def resolve(url, maxwidth=400, maxheight=None):
    provider = get_provider(url)
    if not provider:
        return None
    params = {
        'format': 'json',
        'url': url,
        'maxwidth': provider.get('maxwidth', 400)
    }
    if 'maxheight' in provider:
        params['maxheight'] = provider['maxheight']
    try:
        results = requests.get(provider['url'], params=params)

    except Exception, exc:
        print(exc)
        logger.info(u"Can't resolve oembed for {0} : {1}".format(
            url, unicode(exc))
        )
        raise OEmbedResolutionException()
    try:
        return json.loads(results.content)
    except ValueError:
        logger.info(
            u"Can't resolve oembed for {0} : Json decode error".format(url),
            exc_info=True
        )
        return None
