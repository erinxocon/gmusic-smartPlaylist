# -*- coding: utf-8 -*-
import json
import gmusicapi

from flask import Flask, request, make_response, render_template, g, jsonify

app = Flask(__name__)


def main(d):

    rl = []

    try:
        g.api.login(d['userid'], d['pswrd'])
    except:
        return "Invalid login."

    try:
        l = get_song_list(d)
    except RuntimeError as e:
        return e.message
    except gmusicapi.exceptions.NotLoggedIn:
        return "Invaild Login Credentials"

    if d.get('playCount'):
        min_num = d.get('playCount')
        for track in l:
            if track is not None:
                if track.get('playCount') > int(min_num):
                    if track.get('storeId'):
                        rl.append(track.get('storeId'))
                    else:
                        rl.append(track.get('id'))

    rl = list(set(rl))

    try:
        title = d['title'] if d.get('title') else 'New Playlist'
        playlist = g.api.create_playlist(title)
    except:
        return "Failed to create playlist"

    results = g.api.add_songs_to_playlist(playlist, rl)

    return jsonify(results)


def get_song_list(d):
    l = None

    if d.get('library') is None and d.get('thumbsup') is None \
       and d.get('playlists') is None:

        raise RuntimeError('Please Choose at least one song source.')

    if d.get('library'):
        l = g.api.get_all_songs()

    if d.get('thumbsup'):
        l = [] if l is None else l
        thumbs = g.api.get_thumbs_up_songs()
        for track in thumbs:
            l.append(track)

    if d.get('playlists'):
        l = [] if l is None else l
        playlists = g.api.get_all_user_playlist_contents()
        for playlist in playlists:
            for track in playlist['tracks']:
                track_info = track.get('track')
                l.append(track_info)

    return l


@app.before_request
def before_request():
    g.api = gmusicapi.Mobileclient()


@app.teardown_request
def teardown_request(exception):
    g.api.logout()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return main(request.form)

    return render_template('index.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5280)
    #main(USERNAME, PASSWORD, 30)
