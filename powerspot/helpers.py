"""
General helpers and wrappers to access and modify Spotify user data.
"""

import datetime
import os

import click
import spotipy
from spotipy.util import prompt_for_user_token
from spotipy.oauth2 import SpotifyClientCredentials


def parse_release_date(date):
    """Parses the release date in a datetime object."""
    try:
        output = datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        output = datetime.datetime.strptime(date, '%Y')
    return output


def get_username():
    """Gets or prompts the user for the username."""
    username = None
    # find the username in the cache
    for filename in os.listdir('.'):
        if filename[:6] == '.cache':
            if click.confirm(
                    f"Use cached username '{filename[7:]}'?", default=True
            ):
                username = filename[7:]
                break
    if username is None:
        username = click.prompt("Please enter your username")
    return username


def operation(function):
    """Decorator for spotipy functions that don't need a token."""

    def wrapper(*args, **kwargs):
        credentials = SpotifyClientCredentials()
        sp = spotipy.Spotify(client_credentials_manager=credentials)
        return function(sp, *args, **kwargs)
    return wrapper


def scope_operation(scope):
    """Decorator for spotipy functions that need a token in a given scope."""

    def real_decorator(function):
        def wrapper(username, *args, **kwargs):
            token = prompt_for_user_token(username, scope)
            if token:
                sp = spotipy.Spotify(auth=token)
                return function(sp, *args, **kwargs)
            click.echo(
                click.style(
                    f"Can't get token for {username}", fg='red', bold=True
                )
            )
            return None

        return wrapper

    return real_decorator
