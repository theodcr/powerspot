# powerspot

Command line interface in Python for advanced and automated operations with Spotify, based on the [click](https://github.com/pallets/click) and [spotipy](https://github.com/plamere/spotipy) packages.

## Installation instructions

Not on PyPI, so clone this repo and install the package with `pip install -e .`. This project uses Python >= 3.6.

## Usage

Examples of commands:
```bash
# get all artists from Spotify profile and write them
powerspot artists write artists.json
# get new releases from artists and save them in Spotify library
powerspot artists -f artists.json releases save
# show top tracks
powerspot toptracks show
```
