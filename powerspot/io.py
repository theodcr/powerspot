"""
Input and output functions to store, parse and export Spotify data.
"""

import datetime
from typing import Any, Dict, Iterable, Optional

from tabulate import tabulate

DATE_FORMAT = "%Y-%m-%d"


def parse_artists(
    artists_json: Iterable[Dict[str, Any]], print_date: bool = True
) -> str:
    """Parses artists from JSON format to a readable string.
    Optionally write the current date at beginning of string.
    """
    output = output_date(print_date)
    artists = (artist["name"] for artist in artists_json)
    for artist in artists:
        output += f"- {artist}\n"
    return output


def parse_albums(albums_json: Iterable[Dict[str, Any]], print_date: bool = True) -> str:
    """Parses albums from JSON format to a readable string.
    Optionally write the current date at beginning of string.
    """
    output = output_date(print_date)
    albums = (album["name"] for album in albums_json)
    artists = (album["artists"][0]["name"] for album in albums_json)
    dates = (album["release_date"] for album in albums_json)
    for artist, album, date in zip(artists, albums, dates):
        output += f"- {artist} - {album} - {date}\n"
    return output


def tabulate_albums(
    albums_json: Iterable[Dict[str, Any]], print_date: bool = True
) -> str:
    """Parses albums from JSON format to a string table using tabulate.
    Optionally write the current date at beginning of string.
    """
    output = output_date(print_date)
    albums = (
        (album["artists"][0]["name"], album["name"], album["release_date"])
        for album in albums_json
    )
    output += tabulate(albums, headers=["Artist", "Album", "Date"])
    return output


def tabulate_tracks(
    tracks_json: Iterable[Dict[str, Any]], print_date: bool = True
) -> str:
    """Parses tracks from JSON format to a string table using tabulate.
    Optionally write the current date at beginning of string.
    """
    output = output_date(print_date)
    tracks = (
        (track["artists"][0]["name"], track["name"], track["album"]["name"])
        for track in tracks_json
    )
    output += tabulate(tracks, headers=["Artist", "Track", "Album"])
    return output


def output_date(print_date: bool = True) -> str:
    if print_date:
        return f"%date {datetime.datetime.now().strftime(DATE_FORMAT)}\n"
    return ""


def read_date(filename: str) -> Optional[datetime.datetime]:
    """Reads and returns the date metadata contained in the file.
    Returns None if date could not be found or read.
    """
    with open(filename, "r") as file_content:
        while True:
            words = file_content.readline().split()
            if words[0][1:] == "date":
                date_str = words[1]
                break
    try:
        return datetime.datetime.strptime(date_str, DATE_FORMAT)
    except NameError:
        print("Date could not be found")
    except ValueError:
        print("Date format is invalid")
    return None
