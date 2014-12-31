# -*- coding: utf-8 -*-
import json
import gmusicapi

from flask import Flask, request, jsonify, render_template, g

app = Flask(__name__)


def main(d):

    try:
        g.api.login(d['userid'], d['pswrd'])
    except:
        return "Invalid login."

    try:
        l = get_song_list(d)
    except RuntimeError as e:
        return e.message

    if d.get('playCount'):
        min_num = d.get('playCount')
        for track in l:
            if track.get('playCount') > min_num:
                if track.get('storeId'):
                    l.append(track.get('storeId'))
                else:
                    l.append(track.get('id'))

    l = list(set(l))

    try:
        title = d['title'] if d.get('title') else 'New Playlist'
        playlist = g.api.create_playlist(title)
    except:
        return "Failed to create playlist"

    g.api.add_songs_to_playlist(playlist, l)

    return jsonify(l)


def get_song_list(d):
    l = None

    if d.get('library') is None and d.get('thumbsup') is None \
       and d.get('playlists') is None:

        raise RuntimeError('Please Choose at least one song source.')

    if d.get('library'):
        l = g.api.get_all_songs()

    if d.get('thumbsup'):
        thumbs = g.api.get_thumbs_up_songs()
        for track in thumbs:
            l.append(track)

    if d.get('playlists'):
        playlists = g.api.get_all_user_playlist_contents()
        for playlist in playlists:
            for track in playlist['tracks']:
                track_info = track.get('track')
                try:
                    print track_info['title'], track_info['playCount']
                except:
                    pass

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
    app.run(host='127.0.0.1', port=5280)
    #main(USERNAME, PASSWORD, 30)
