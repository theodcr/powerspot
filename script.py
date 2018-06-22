# coding: utf-8

import datetime
import json
import os
import pprint
import sys
import spotipy
import spotipy.util as util


INTERVAL = datetime.timedelta(weeks=4)


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
        username = raw_input("Please enter your username: ")
    return username


def operation(function):
    """Decorator for spotipy functions that don't need a token"""
    def wrapper(*args, **kwargs):
        sp = spotipy.Spotify(auth=token)
        return function(sp, *args, **kwargs)
    return wrapper


def authorized_operation(scope):
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


@authorized_operation('user-follow-read')
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


@authorized_operation('user-follow-read')
def get_new_releases(sp, artists, interval=INTERVAL):
    """Returns a list of recently released albums"""
    new_releases = []
    for artist in artists:
        results = sp.artist_albums(artist['id'])
        # only use last album
        album = results['items'][0]
        release_date = parse_release_date(album['release_date'])
        if release_date > datetime.datetime.now() - interval:
            new_releases.append(album)
    return new_releases


@authorized_operation('user-library-modify')
def save_albums(sp, albums):
    """Saves the albums in the user library"""
    ids = [album['id'] for album in albums]
    results = sp.current_user_saved_albums_add(ids)
    return results


def parse_albums(albums_json):
    """Parses albums from JSON format to a readable list"""
    output = ""
    albums = (album['name'] for album in albums_json)
    artists = (album['artists'][0]['name'] for album in albums_json)
    dates = (album['release_date'] for album in albums_json)
    for artist, album, date in zip(artists, albums, dates):
        output += "- {} - {} - {}\n".format(artist, album, date)
    return output


def main():
    username = get_username()
    #artists = get_followed_artists(username)
    #new_releases = get_new_releases(username, artists)
    #write_json(artists, "artists.json")
    new_releases = read_json("new_releases.json")
    write_file(parse_albums(new_releases), "new_releases.wiki")


if __name__ == '__main__':
    main()
