#!/usr/bin/env python3
"""
Main script to call functions from the CLI.
Click context can contain:
- `artists` as json string
- `albums` as json string
- `export` which is the result from the last command in the pipe
"""

import json
import os

import click

from powerspot import helpers, io, operations, ui


@click.group(chain=True)
@click.option('--username', default=lambda: os.getenv('SPOTIFY_USER'))
@click.pass_context
def main(ctx, username):
    """CLI for advanced and automated operations with Spotify."""
    click.echo(click.style(ui.GREET, fg='magenta', bold=True))

    if username is None:
        username = helpers.get_username()

    click.echo(click.style(f"Welcome {username}\n", fg='blue'))
    ctx.obj = {}
    ctx.obj['username'] = username


@main.command()
@click.option('--file', '-f', type=click.File('r'))
@click.pass_context
@ui.echo_feedback("Fetching saved albums...", "Albums fetched!")
def albums(ctx, file):
    """Fetches saved albums from Spotify user library."""
    if file is not None:
        albums = json.load(file)
    else:
        albums = operations.get_saved_albums(ctx.obj['username'])
    ctx.obj['albums'] = albums
    ctx.obj['export'] = albums


@main.command()
@click.option('--file', '-f', type=click.File('r'))
@click.pass_context
@ui.echo_feedback("Fetching artists...", "Artists fetched!")
def artists(ctx, file):
    """Fetches artists from file or Spotify profile."""
    if file is not None:
        artists = json.load(file)
    else:
        artists = operations.get_followed_artists(ctx.obj['username'])
    ctx.obj['artists'] = artists
    ctx.obj['export'] = artists


@main.command()
@click.option('--file', '-f', type=click.File('r'))
@click.option('--read-date', '-r', type=click.Path(exists=True))
@click.option('--weeks', '-w', type=click.IntRange(1))
@click.pass_context
@ui.echo_feedback("Fetching releases from Spotify...", "Releases fetched!")
def releases(ctx, file, read_date, weeks):
    """Fetches new releases from given artists."""
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
                weeks = click.prompt(
                    "Fetch time interval in weeks", type=int, default=4
                )
        if 'artists' in ctx.obj:
            new_releases = operations.get_new_releases(
                ctx.obj['artists'], date=date, weeks=weeks
            )
        else:
            click.echo("Artists not in context, discarding", err=True)
        click.echo(io.tabulate_albums(new_releases, print_date=False))
    ctx.obj['albums'] = new_releases
    ctx.obj['export'] = new_releases


@main.command()
@click.option(
    '--term',
    '-t',
    default='long',
    show_default=True,
    help='fetch long/medium/short term tops',
)
@click.pass_context
@ui.echo_feedback("Fetching top artists...", "Artists fetched!")
def topartists(ctx, term):
    """Fetches user top artists from Spotify profile."""
    time_range = f'{term}_term'
    artists = operations.get_top_artists(ctx.obj['username'], time_range=time_range)
    ctx.obj['artists'] = artists
    ctx.obj['export'] = artists


@main.command()
@click.option(
    '--term',
    '-t',
    default='long',
    show_default=True,
    help='fetch long/medium/short term tops',
)
@click.pass_context
@ui.echo_feedback("Fetching top tracks...", "Tracks fetched!")
def toptracks(ctx, term):
    """Fetches user top tracks from Spotify profile."""
    time_range = f'{term}_term'
    tracks = operations.get_top_tracks(ctx.obj['username'], time_range=time_range)
    ctx.obj['tracks'] = tracks
    ctx.obj['export'] = tracks


@main.command()
@click.option('--ask', '-a', is_flag=True, help='ask which albums to save')
@click.pass_context
@ui.echo_feedback("Saving releases to account...", "Releases saved!")
def save(ctx, ask):
    """Saves albums in the Spotify user library."""
    if ask:
        albums_to_save = []
        for album in ctx.obj['albums']:
            click.echo(
                click.style(album['artists'][0]['name'], fg='magenta', bold=True)
                + click.style(' - ', fg='white')
                + click.style(album['name'], fg='blue', bold=True)
            )
            if click.confirm("Save album", default=True):
                albums_to_save.append(album)
    else:
        albums_to_save = ctx.obj['albums']
    operations.save_albums(ctx.obj['username'], albums_to_save)


@main.command()
@click.argument('file', type=click.File('w'))
@click.pass_context
@ui.echo_feedback("Writing to file...", "Done!")
def write(ctx, file):
    """Writes the results from the last command to a JSON or wiki file."""
    if file.name.split('.')[-1] == 'wiki':
        file.write(io.tabulate_albums(ctx.obj['export']))
    else:
        file.write(json.dumps(ctx.obj['export']))


if __name__ == '__main__':
    main()
