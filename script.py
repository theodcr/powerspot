#!/usr/bin/env python3
"""Collection of functions to enhance the Spotify experience"""

import datetime
import json
import os
import pprint
import spotipy
import spotipy.util as util


datapath = lambda path: "data/" + path
exportpath = lambda path: "export/" + path
date_format = '%Y-%m-%d'


def parse_release_date(date):
    """Parses the release date in a datetime object"""
    try:
        output = datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        output = datetime.datetime.strptime(date, '%Y')
    return output


def write_file(content, filename):
    """Writes the given content in a file"""
    with open(filename, 'w') as file_content:
        file_content.write(content)


def read_json(filename):
    """Reads the content of a JSON file"""
    with open(filename, 'r') as file_content:
        content = json.load(file_content)
    return content


def write_json(content, filename):
    """Writes the given content in a JSON file"""
    with open(filename, 'w') as file_content:
        file_content.write(json.dumps(content))


def get_username():
    """Gets or prompts the user for the username"""
    username = os.getenv('SPOTIFY_USER')
    if username is None:
        # find the username in the cache
        for filename in os.listdir('.'):
            if filename[:6] == '.cache':
                is_username = raw_input(
                    f"Use cached username '{filename[7:]}'? (y) ")
                if is_username == 'y':
                    username = filename[7:]
                    break
    if username is None:
        username = raw_input("Please enter your username: ")
    return username


def operation(function):
    """Decorator for spotipy functions that don't need a token"""
    def wrapper(*args, **kwargs):
        sp = spotipy.Spotify()
        return function(sp, *args, **kwargs)
    return wrapper


def authenticated_operation(scope):
    """Decorator for spotipy functions that need a token"""
    def real_decorator(function):
        def wrapper(username, *args, **kwargs):
            token = util.prompt_for_user_token(username, scope)
            if token:
                sp = spotipy.Spotify(auth=token)
                return function(sp, *args, **kwargs)
            else:
                print("Can't get token for", username)
                return None
        return wrapper
    return real_decorator


@operation
def get_album(sp, album_id):
    """Returns an album given its ID or URI"""
    return sp.album(album_id)


@authenticated_operation('user-follow-read')
def get_followed_artists(sp):
    """Returns the full list of followed artists"""
    artists = []
    results = sp.current_user_followed_artists(limit=50)['artists']
    artists.extend(results['items'])
    while results['next']:
        results = sp.next(results)['artists']
        artists.extend(results['items'])
    artists.sort(key=lambda artist:artist['name'].lower())
    return artists


@authenticated_operation('user-follow-read')
def get_new_releases(sp, artists, date=None):
    """Returns a list of released albums since the a given date
    If no date is given, it considers the last 4 weeks"""
    if date is None:
        date = datetime.datetime.now() - datetime.timedelta(weeks=4)
    new_releases = []
    for artist in artists:
        results = sp.artist_albums(artist['id'])
        # only use last album
        album = results['items'][0]
        release_date = parse_release_date(album['release_date'])
        if release_date > date:
            new_releases.append(album)
    return new_releases


@authenticated_operation('user-library-modify')
def save_albums(sp, albums):
    """Saves the albums in the user library"""
    ids = [album['id'] for album in albums]
    results = sp.current_user_saved_albums_add(ids)
    return results


def parse_albums(albums_json, write_date=True):
    """Parses albums from JSON format to a readable list
    Optionally write the current date"""
    output = ""
    if write_date:
        output += f"%date {datetime.datetime.now().strftime(date_format)}\n"
    albums = (album['name'] for album in albums_json)
    artists = (album['artists'][0]['name'] for album in albums_json)
    dates = (album['release_date'] for album in albums_json)
    for artist, album, date in zip(artists, albums, dates):
        output += f"- {artist} - {album} - {date}\n"
    return output


def read_date(filename):
    """Reads and returns the date metadata contained in the file
    Returns None if date could not be found or read"""
    with open(filename, 'r') as file_content:
        while True:
            words = file_content.readline().split()
            if words[0][1:] == 'date':
                date_str = words[1]
                break
    try:
        date = datetime.datetime.strptime(date_str, date_format)
    except:
        date = None
    return date


def main():
    username = get_username()
    #artists = get_followed_artists(username)
    #write_json(artists, datapath("artists.json"))
    #new_releases = get_new_releases(username, artists)
    new_releases = read_json(datapath("new_releases.json"))
    write_file(parse_albums(new_releases),
               exportpath("new_releases.wiki"))
    return username


if __name__ == '__main__':
    main()
