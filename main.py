#!/usr/bin/env python3
"""Enhance the Spotify experience
Main script to calls functions from the CLI"""

import pprint
from powerspot import io, spotify


def main():
    username = spotify.get_username()
    #artists = get_followed_artists(username)
    #write_json(artists, io.datapath("artists.json"))
    artists = io.read_json(io.datapath("artists.json"))
    #new_releases = read_json(io.datapath("new_releases.json"))
    last_export_date = io.read_date(io.exportpath("new_releases.wiki"))
    #new_releases = get_new_releases(username, artists, last_export_date)
    new_releases = io.read_json(io.datapath("new_releases.json"))
    #write_json(new_releases, io.datapath("new_releases.json"))
    #write_file(parse_albums(new_releases),
    #           io.exportpath("new_releases.wiki"))
    print(io.parse_albums(new_releases, print_date=False))
    #save_albums(username, new_releases)
    return username


if __name__ == '__main__':
    main()
