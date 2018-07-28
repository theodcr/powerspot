"""Functions that access the Spotify account to retrieve data or modify
the user library"""

import datetime
import os
import click
import spotipy
import spotipy.util


def parse_release_date(date):
    """Parses the release date in a datetime object"""
    try:
        output = datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        output = datetime.datetime.strptime(date, '%Y')
    return output


def get_username():
    """Gets or prompts the user for the username"""
    username = os.getenv('SPOTIFY_USER')
    if username is None:
        # find the username in the cache
        for filename in os.listdir('.'):
            if filename[:6] == '.cache':
                is_username = input(
                    f"Use cached username '{filename[7:]}'? (y) ")
                if is_username == 'y':
                    username = filename[7:]
                    break
    if username is None:
        username = input("Please enter your username: ")
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
            token = spotipy.util.prompt_for_user_token(username, scope)
            if token:
                sp = spotipy.Spotify(auth=token)
                return function(sp, *args, **kwargs)
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
    artists.sort(key=lambda artist: artist['name'].lower())
    return artists


@authenticated_operation('user-follow-read')
def get_new_releases(sp, artists, date=None):
    """Returns a list of released albums since the a given date
    If no date is given, it considers the last 4 weeks"""
    if date is None:
        date = datetime.datetime.now() - datetime.timedelta(weeks=4)
    new_releases = []
    with click.progressbar(artists) as progress_bar:
        for artist in progress_bar:
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
