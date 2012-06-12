def get_widget(url, *args, **kwargs):
    full_url = 'http://twitpic.com/show/full/' + url.replace('http://twitpic.com/', '')
    return '<a href="%s"><img src="%s" /></a>' % (url, full_url)

def get_host():
    return ['twitpic.com']

def get_tag():
    return "twitpic"

if __name__ == '__main__':
    # get a tracks oembed data
    track_url = 'http://twitpic.com/9vfzqv'
    print get_widget(track_url)
