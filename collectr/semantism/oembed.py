import json
import logging
import re
import requests


PROVIDERS = {
    'youtube': ('http://www.youtube.com/oembed', [".*youtube.*\watch\?v\=.*"]),
    'vimeo': ('http://vimeo.com/api/oembed.json', ['^http:\/\/.vimeo\.com\/\d+', 'http:\/\/www\.vimeo\.com\/groups\/.*\/videos\/.*', 'http:\/\/www\.vimeo\.com\/.*', 'http:\/\/vimeo\.com\/groups\/.*\/videos\/.*', 'http:\/\/vimeo\.com\/.*']),
    'flickr': ('http://flickr.com/services/oembed', ['flickr\\.com/photos/[-.\\w@]+/\\d+/?']),
    'instagram': ('http://api.instagram.com/oembed', ['^http:\/\/instagr.am\/p\/.*', '^http:\/\/instagram\.com\/p\/.*']),
    'dailymotion': ('http://www.dailymotion.com/services/oembed', ['.*.www\.dailymotion\.com\/video\/.*']),
    'soundcloud': ('http://soundcloud.com/oembed', ['^.*:\/\/soundcloud.com/.*/.*']),
}


logger = logging.getLogger(__name__)


class OEmbedResolutionException(Exception):
    pass


def get_provider(url):
    for provider, infos in PROVIDERS.items():
        for regex in infos[1]:
            if re.match(regex, url):
                return infos[0]
    return None


def resolve(url, maxwidth=400, maxheight=None):
    provider_url = get_provider(url)
    if not provider_url:
        return None
    params = {'url': url, 'format': 'json'}
    if maxwidth:
        params['maxwidth'] = maxwidth
    if maxheight:
        params['maxheight'] = maxheight

    try:
        results = requests.get(provider_url, params=params)
    except Exception, exc:
        logger.info(u"Can't resolve oembed for {0} : {1}".format(url, unicode(exc)))
        raise OEmbedResolutionException()
    try:
        return json.loads(results.content)
    except ValueError:
        logger.info(u"Can't resolve oembed for {0} : Json decode error".format(url), exc_info=True)
        return None
