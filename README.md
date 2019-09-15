# powerspot

Command line interface and API in Python for advanced and automated operations with Spotify, based on the [click](https://github.com/pallets/click) and [spotipy](https://github.com/plamere/spotipy) packages.

## Installation instructions

This project uses Python >= 3.6.

```
pip install powerspot
```

## Usage

Examples of commands:
```bash
# get followed artists from Spotify profile and write them
powerspot artists write artists.json

# get new releases from those artists and save them in Spotify library
powerspot artists -f artists.json releases save

# show top tracks from recent activity
powerspot toptracks --term short show
```
