import soundcloud


def get_widget(url, *args, **kwargs):
    # Create a new client that uses the user credentials oauth flow
    print dir(soundcloud)
    client = soundcloud.Client(client_id='b497591ca4a727ce38ad23a56e3e9148',
                               client_secret='d52425370782df4f7c72794fdb1fe49a',
                               username='user8157534',
                               password='snnbzwxbrp')

    # get a tracks oembed data
    track_url = 'http://soundcloud.com/forss/flickermood'
    embed_info = client.get('/oembed', url=track_url)
    return embed_info.fields()['html']

def get_host():
    return ['soundcloud.com', 'www.soundcloud.com']

def get_tag():
    return "soundcloud"

if __name__ == '__main__':
    # get a tracks oembed data
    track_url = 'http://soundcloud.com/forss/flickermood'
    print get_widget(track_url)
