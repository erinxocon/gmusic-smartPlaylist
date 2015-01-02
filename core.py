# -*- coding: utf-8 -*-
import gmusicapi

from flask import g, jsonify
from datetime import datetime


def main(request_args):
    #pull filter vars from request_args
    play_count = request_args.get('play_count')
    artists = request_args.get('artist')
    albums = request_args.get('album')

    #create empyt song list in case they don't select my library
    song_list = []

    #try to login and catch error if login creds are missing or wrong
    try:
        g.api.login(request_args['userid'], request_args['pswrd'])
    except:
        return "Invalid login."

    #Get song list based on request_args
    try:
        song_list = get_song_list(request_args)
    except RuntimeError as e:
        return e.message
    except gmusicapi.exceptions.NotLoggedIn:
        return "Invaild Login Credentials"

    #Preform filter functions based on request_args
    if play_count:
        song_list = play_count_filter(play_count, song_list[:])

    if artists:
        song_list = artist_filter(artists, song_list[:])

    if albums:
        song_list = album_filter(albums, song_list[:])

    #extract song_ids from track listings
    song_id_list = extract_song_ids(song_list)

    #create title for playlist
    ts = datetime.now().strftime('%x %X')
    title = request_args['title'] if request_args.get('title') else ts

    #try and create the playlist
    try:
        playlist = g.api.create_playlist(title)
    except:
        return "Failed to create playlist"

    #remove duplicates from song list
    song_id_list = list(set(song_id_list))

    #create playlist with chosen songs
    g.api.add_songs_to_playlist(playlist, song_id_list)

    return jsonify(play_count=play_count, artist=artists, album=albums,
                   song=song_id_list)


def play_count_filter(play_count_min, song_list):

    results = []

    for track in song_list:
        if track is not None:
            if track.get('playCount') > int(play_count_min):
                results.append(track)

    return results


def artist_filter(artists, song_list):

    results = []

    artist_list = map(lambda x: x.lower(), artists.split(','))

    for track in song_list:
        if track is not None:
            if track.get('artist').lower() in artist_list:
                results.append(track)

    return results


def album_filter(albums, song_list):

    results = []

    album_list = map(lambda x: x.lower(), albums.split(','))

    for track in song_list:
        if track is not None:
            if track.get('artist') in album_list:
                results.append(track)

    return results


def extract_song_ids(song_list):

    results = []

    for track in song_list:
        if track is not None:
            if track.get('storeId'):
                results.append(track['storeId'])

            else:
                results.append(track['id'])

    return results


def get_song_list(d):

    song_list = []

    if d.get('library') is None and d.get('thumbsup') is None \
       and d.get('playlists') is None:

        raise RuntimeError('Please Choose at least one song source.')

    if d.get('library'):
        song_list = g.api.get_all_songs()

    if d.get('thumbsup'):
        thumbs = g.api.get_thumbs_up_songs()
        for track in thumbs:
            song_list.append(track)

    if d.get('playlists'):
        playlists = g.api.get_all_user_playlist_contents()
        for playlist in playlists:
            for track in playlist['tracks']:
                track_info = track.get('track')
                song_list.append(track_info)

    return song_list
