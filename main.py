#!/usr/bin/env python3
"""Enhance the Spotify experience
Main script to calls functions from the CLI
Click context can contain:
- artists as json string
- new releases as json string
- export, which is the result from the last command in the pipe
"""

from functools import update_wrapper
import json
import os
import click
from powerspot import io, spotify


GREET = """
    ____                          _____             __
   / __ \____ _      _____  _____/ ___/____  ____  / /_
  / /_/ / __ \ | /| / / _ \/ ___/\__ \/ __ \/ __ \/ __/
 / ____/ /_/ / |/ |/ /  __/ /   ___/ / /_/ / /_/ / /_
/_/    \____/|__/|__/\___/_/   /____/ .___/\____/\__/
                                   /_/
"""


@click.group(chain=True)
@click.option('--username',
              default=lambda: os.getenv('SPOTIFY_USER'))
@click.pass_context
def main(ctx, username):
    """Enhance the Spotify experience"""
    click.echo(click.style(
        GREET,
        fg='magenta', bold=True))
    click.echo(click.style(
        "Enhance the Spotify experience",
        fg='magenta', bold=True))

    if username is None:
        username = spotify.get_username()

    click.echo(click.style(
        f"Welcome {username}\n",
        fg='blue'))
    ctx.obj = {}
    ctx.obj['username'] = username


def echo_feedback(before, after):
    def pass_obj(function):
        @click.pass_context
        def wrapper(ctx, *args, **kwargs):
            click.echo(click.style(before, fg='cyan'))
            ctx.invoke(function, *args, **kwargs)
            click.echo(click.style(f"{after}\n", fg='blue', bold=True))
        return update_wrapper(wrapper, function)
    return pass_obj


@main.command()
@click.option('--file', '-f', type=click.File('r'))
@click.pass_context
@echo_feedback("Fetching artists...", "Artists fetched!")
def artists(ctx, file):
    """Fetches artists from Spotify profile"""
    if file is not None:
        artists = json.load(file)
    else:
        artists = spotify.get_followed_artists(ctx.obj['username'])
    ctx.obj['artists'] = artists
    ctx.obj['export'] = artists


@main.command()
@click.option('--file', '-f', type=click.File('r'))
@click.option('--read-date', '-r', type=click.Path(exists=True))
@click.option('--weeks', '-w', type=click.IntRange(1))
@click.pass_context
@echo_feedback("Fetching releases from Spotify...", "Releases fetched!")
def releases(ctx, file, read_date, weeks):
    """Fetches new releases from given artists"""
    if file is not None:
        new_releases = json.load(file)
    else:
        # Uses date from optional file, else uses the weeks option
        # else prompts for a number of weeks
        if read_date is not None:
            date = io.read_date(read_date)
            weeks = None
        else:
            date = None
            if weeks is None:
                weeks = click.prompt("Fetch time interval in weeks",
                                     type=int, default=4)
        if 'artists' in ctx.obj:
            new_releases = spotify.get_new_releases(
                ctx.obj['username'],
                ctx.obj['artists'],
                date=date,
                weeks=weeks)
        else:
            click.echo("Artists not in context, discarding", err=True)
        click.echo(io.tabulate_albums(new_releases, print_date=False))
    ctx.obj['new_releases'] = new_releases
    ctx.obj['export'] = new_releases


@main.command()
@click.pass_context
@echo_feedback("Saving releases to account...", "Releases saved!")
def save(ctx):
    """Saves new releases in the Spotify profile"""
    spotify.save_albums(ctx.obj['username'], ctx.obj['new_releases'])


@main.command()
@click.argument('file', type=click.File('w'))
@echo_feedback("Writing to file...", "Done!")
@click.pass_context
def write(ctx, file):
    """Writes the results from the last command to a json or wiki file"""
    if file.name.split('.')[-1] == 'wiki':
        file.write(io.tabulate_albums(ctx.obj['export']))
    else:
        file.write(json.dumps(ctx.obj['export']))


if __name__ == '__main__':
    main()
