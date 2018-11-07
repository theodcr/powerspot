"""
Functions that access the Spotify account to retrieve data or modify
the user library
"""

import datetime
import click

from .helpers import operation, parse_release_date, scope_operation


@operation
def get_album(sp, album_id):
    """Returns an album given its ID or URI"""
    return sp.album(album_id)


@operation
def search_artist_album(sp, artist, album, limit=5):
    """Returns the search results for albums given an artist and an album"""
    query = f'album:{album} artist:{artist}'
    return sp.search(query, limit=limit, type='album')['albums']


@operation
def search_artist(sp, artist, limit=5):
    """Returns the search results for artists given an artist query"""
    query = f'artist:{artist}'
    return sp.search(query, limit=limit, type='artist')['artists']


@operation
def get_artist_albums(sp, artist_id, album_type='album', limit=20):
    """Returns the albums of an artist given its ID or URI"""
    return sp.artist_albums(artist_id, album_type=album_type)


@scope_operation('user-follow-read')
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


@scope_operation('user-follow-read')
def get_new_releases(sp, artists, date=None, weeks=4):
    """Returns a list of released albums from the given artists
    since the a given date (first choice) or during a given interval"""
    if date is None:
        date = datetime.datetime.now() - datetime.timedelta(weeks=weeks)
    new_releases = []
    click.echo(f"Fetching from {date.strftime('%Y-%m-%d')}")
    with click.progressbar(
        artists, label="Fetching new releases"
    ) as progress_bar:
        for artist in progress_bar:
            results = sp.artist_albums(artist['id'])
            # only use last album
            album = results['items'][0]
            release_date = parse_release_date(album['release_date'])
            if release_date > date:
                new_releases.append(album)
    return new_releases


@scope_operation('user-library-read')
def get_saved_albums(sp):
    """Returns a list of albums saved in user library"""
    albums = []
    results = sp.current_user_saved_albums(limit=50)
    albums.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
    return albums


@scope_operation('user-library-modify')
def save_albums(sp, albums):
    """Saves the albums in the user library"""
    ids = [album['id'] for album in albums]
    results = sp.current_user_saved_albums_add(ids)
    return results
