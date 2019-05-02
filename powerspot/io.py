"""
Input and output functions to store, parse and export Spotify data.
"""

import datetime
import json
from tabulate import tabulate

DATE_FORMAT = '%Y-%m-%d'


def write_file(content, filename):
    """Writes the given content in a file."""
    with open(filename, 'w') as file_content:
        file_content.write(content)


def read_json(filename):
    """Reads the content of a JSON file."""
    with open(filename, 'r') as file_content:
        content = json.load(file_content)
    return content


def write_json(content, filename):
    """Writes the given content in a JSON file."""
    with open(filename, 'w') as file_content:
        file_content.write(json.dumps(content))


def parse_albums(albums_json, print_date=True):
    """Parses albums from JSON format to a readable string.
    Optionally write the current date at beginning of string.
    """
    output = ""
    if print_date:
        output += f"%date {datetime.datetime.now().strftime(DATE_FORMAT)}\n"
    albums = (album['name'] for album in albums_json)
    artists = (album['artists'][0]['name'] for album in albums_json)
    dates = (album['release_date'] for album in albums_json)
    for artist, album, date in zip(artists, albums, dates):
        output += f"- {artist} - {album} - {date}\n"
    return output


def tabulate_albums(albums_json, print_date=True):
    """Parses albums from JSON format to a string table using tabulate.
    Optionally write the current date at beginning of string.
    """
    output = ""
    if print_date:
        output += f"%date {datetime.datetime.now().strftime(DATE_FORMAT)}\n"
    albums = (
        (album['artists'][0]['name'], album['name'], album['release_date'])
        for album in albums_json
    )
    output += tabulate(albums, headers=['Artist', 'Album', 'Date'])
    return output


def read_date(filename):
    """Reads and returns the date metadata contained in the file.
    Returns None if date could not be found or read.
    """
    with open(filename, 'r') as file_content:
        while True:
            words = file_content.readline().split()
            if words[0][1:] == 'date':
                date_str = words[1]
                break
    try:
        return datetime.datetime.strptime(date_str, DATE_FORMAT)
    except NameError:
        print("Date could not be found")
    except ValueError:
        print("Date format is invalid")
