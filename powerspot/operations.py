"""
Functions that access the Spotify account to retrieve data or modify
the user library
"""

import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import click
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.util import prompt_for_user_token


def operation(function: Callable) -> Callable:
    """Decorator for spotipy functions that don't need a token."""

    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Callable:
        credentials = SpotifyClientCredentials()
        sp = Spotify(client_credentials_manager=credentials)
        return function(sp, *args, **kwargs)

    return wrapper


def scope_operation(scope: str) -> Callable:
    """Decorator for spotipy functions that need a token in a given scope."""

    def real_decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(username: str, *args: Any, **kwargs: Any) -> None:
            token = prompt_for_user_token(username, scope)
            if token:
                sp = Spotify(auth=token)
                return function(sp, *args, **kwargs)
            click.echo(
                click.style(f"Can't get token for {username}", fg="red", bold=True)
            )
            return None

        return wrapper

    return real_decorator


def parse_release_date(date: str) -> datetime.datetime:
    """Parses the release date in a datetime object."""
    try:
        output = datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        output = datetime.datetime.strptime(date, "%Y")
    return output


@operation
def get_album(sp: Spotify, album_id: str) -> Dict[str, Any]:
    """Returns an album given its ID or URI"""
    return sp.album(album_id)


@operation
def get_artist(sp: Spotify, artist_id: str) -> Dict[str, Any]:
    """Returns an artist given its ID or URI"""
    return sp.artist(artist_id)


@operation
def get_track(sp: Spotify, track_id: str) -> Dict[str, Any]:
    """Returns an track given its ID or URI"""
    return sp.track(track_id)


@operation
def get_tracks(sp: Spotify, track_ids: List[str]) -> List[Dict[str, Any]]:
    """Returns tracks given their ID or URI"""
    return sp.tracks(track_ids)


@operation
def get_audio_features(sp: Spotify, track_ids: List[str]) -> List[Dict[str, Any]]:
    """Returns audio features for tracks given their ID or URI"""
    return sp.audio_features(track_ids)


@operation
def get_audio_analysis(sp: Spotify, track_id: str) -> Dict[str, Any]:
    """Returns audio analysis for track given its ID or URI"""
    return sp.audio_analysis(track_id)


@operation
def get_artist_albums(
    sp: Spotify,
    artist_id: str,
    album_type: str = "album",
    country: str = "FR",
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Returns the albums of an artist given its ID or URI"""
    return sp.artist_albums(artist_id, album_type=album_type, country=country)["items"]


@operation
def search_album(
    sp: Spotify,
    album: str,
    artist: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Returns the search results for albums given an album query
    Artist and year are optional
    """
    query = f"album:{album}"
    if artist is not None:
        query += f" artist:{artist}"
    if year is not None:
        query += f" year:{year}"
    return sp.search(query, limit=limit, type="album")["albums"]


@operation
def search_artist(sp: Spotify, artist: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Returns the search results for artists given an artist query"""
    query = f"artist:{artist}"
    return sp.search(query, limit=limit, type="artist")["artists"]


@scope_operation("user-follow-read")
def get_followed_artists(sp: Spotify) -> List[Dict[str, Any]]:
    """Returns the full list of followed artists"""
    artists = []  # type: List[Dict[str, Any]]
    results = sp.current_user_followed_artists(limit=50)["artists"]
    artists.extend(results["items"])
    while results["next"]:
        results = sp.next(results)["artists"]
        artists.extend(results["items"])
    artists.sort(key=lambda artist: artist["name"].lower())
    return artists


@operation
def get_new_releases(
    sp: Spotify,
    artists: List[Dict[str, Any]],
    date: Optional[datetime.datetime] = None,
    weeks: int = 4,
    album_type: str = "album",
    country: str = "FR",
) -> List[Dict[str, Any]]:
    """Returns a list of released albums from the given artists
    since the a given date (first choice) or during a given interval"""
    if date is None:
        date = datetime.datetime.now() - datetime.timedelta(weeks=weeks)
    new_releases = []
    click.echo(f"Fetching from {date.strftime('%Y-%m-%d')}")
    with click.progressbar(artists, label="Fetching new releases") as progress_bar:
        for artist in progress_bar:
            results = sp.artist_albums(
                artist["id"], album_type=album_type, country=country, limit=1
            )["items"]
            if len(results) == 0:
                continue
            # only get last album
            album = results[0]
            release_date = parse_release_date(album["release_date"])
            if release_date > date:
                new_releases.append(album)
    return new_releases


@scope_operation("user-library-read")
def get_saved_albums(sp: Spotify) -> List[Dict[str, Any]]:
    """Returns the list of albums saved in user library"""
    albums = []  # type: List[Dict[str, Any]]
    results = sp.current_user_saved_albums(limit=50)
    albums.extend(results["items"])
    while results["next"]:
        results = sp.next(results)
        albums.extend(results["items"])
    return albums


@scope_operation("user-library-read")
def get_saved_tracks(sp: Spotify) -> List[Dict[str, Any]]:
    """Returns the list of tracks saved in user library"""
    tracks = []  # type: List[Dict[str, Any]]
    results = sp.current_user_saved_tracks(limit=50)
    tracks.extend(results["items"])
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])
    return tracks


@scope_operation("user-library-modify")
def save_albums(sp: Spotify, albums: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Saves the albums in the user library"""
    ids = [album["id"] for album in albums]
    results = sp.current_user_saved_albums_add(ids)
    return results


@scope_operation("user-top-read")
def get_top_artists(
    sp: Spotify, time_range: str = "long_term", limit: int = 20
) -> List[Dict[str, Any]]:
    """Get user top artists"""
    results = sp.current_user_top_artists(limit=limit, time_range=time_range)["items"]
    return results


@scope_operation("user-top-read")
def get_top_tracks(
    sp: Spotify, time_range: str = "long_term", limit: int = 20
) -> List[Dict[str, Any]]:
    """Get user top tracks"""
    results = sp.current_user_top_tracks(limit=limit, time_range=time_range)["items"]
    return results
