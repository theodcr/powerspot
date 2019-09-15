#!/usr/bin/env python3
"""
Main script to call functions from the CLI.
Click context can contain:
- `username` as a string
- `artists` as json string
- `albums` as json string
- `tracks` as json string
- `export` which is the result from the last command in the pipe
- `last` which is the type of data in export (artists, albums, tracks etc)
"""

import json
import os

import click

from _io import TextIOWrapper
from powerspot import io, operations, ui

PARSERS = {
    "tracks": io.tabulate_tracks,
    "artists": io.parse_artists,
    "albums": io.tabulate_albums,
}


def get_username(directory: str = ".") -> str:
    """Gets or prompts the user for the username."""
    username = None
    # find the username in the cache
    for filename in os.listdir(directory):
        if filename[:6] == ".cache":
            if click.confirm(f"Use cached username '{filename[7:]}'?", default=True):
                username = filename[7:]
                break
    if username is None:
        username = click.prompt("Please enter your username")
    return username


@click.group(chain=True)
@click.option("--username", default=lambda: os.getenv("SPOTIFY_USER"))
@click.pass_context
def main(ctx: click.Context, username: str) -> None:
    """CLI for advanced and automated operations with Spotify."""
    click.echo(click.style(ui.GREET, fg="magenta", bold=True))

    if username is None:
        username = get_username()

    click.echo(click.style(f"Welcome {username}\n", fg="blue"))
    ctx.obj = {}
    ctx.obj["username"] = username


@main.command()
@click.option("--file", "-f", type=click.File("r"))
@click.pass_context
@ui.echo_feedback("Fetching albums...", "Albums fetched!")
def albums(ctx: click.Context, file: TextIOWrapper) -> None:
    """Fetches albums from file or Spotify user library."""
    if file is not None:
        albums = json.load(file)
    else:
        albums = operations.get_saved_albums(ctx.obj["username"])
        albums = [album["album"] for album in albums]
    ctx.obj["albums"] = albums
    ctx.obj["export"] = albums
    ctx.obj["last"] = "albums"


@main.command()
@click.option("--file", "-f", type=click.File("r"))
@click.pass_context
@ui.echo_feedback("Fetching artists...", "Artists fetched!")
def artists(ctx: click.Context, file: TextIOWrapper) -> None:
    """Fetches artists from file or Spotify profile."""
    if file is not None:
        artists = json.load(file)
    else:
        artists = operations.get_followed_artists(ctx.obj["username"])
    ctx.obj["artists"] = artists
    ctx.obj["export"] = artists
    ctx.obj["last"] = "artists"


@main.command()
@click.option("--file", "-f", type=click.File("r"))
@click.pass_context
@ui.echo_feedback("Fetching tracks...", "Tracks fetched!")
def tracks(ctx: click.Context, file: TextIOWrapper) -> None:
    """Fetches tracks from file or Spotify user library."""
    if file is not None:
        tracks = json.load(file)
    else:
        tracks = operations.get_saved_tracks(ctx.obj["username"])
        tracks = [track["track"] for track in tracks]
    ctx.obj["tracks"] = tracks
    ctx.obj["export"] = tracks
    ctx.obj["last"] = "tracks"


@main.command()
@click.option("--file", "-f", type=click.File("r"))
@click.option("--read-date", "-r", type=click.Path(exists=True))
@click.option("--weeks", "-w", type=click.IntRange(1))
@click.pass_context
@ui.echo_feedback("Fetching releases from Spotify...", "Releases fetched!")
def releases(
    ctx: click.Context, file: TextIOWrapper, read_date: TextIOWrapper, weeks: int
) -> None:
    """Fetches new releases from artists from last command."""
    if file is not None:
        new_releases = json.load(file)
    else:
        # Uses date from optional file, else uses the weeks option
        # else prompts for a number of weeks
        if read_date is not None:
            date = io.read_date(read_date)
        else:
            date = None
            if weeks is None:
                weeks = click.prompt(
                    "Fetch time interval in weeks", type=int, default=4
                )
        if "artists" in ctx.obj:
            new_releases = operations.get_new_releases(
                ctx.obj["artists"], date=date, weeks=weeks
            )
        else:
            click.echo("Artists not in context, discarding", err=True)
    ctx.obj["albums"] = new_releases
    ctx.obj["export"] = new_releases
    ctx.obj["last"] = "albums"


@main.command()
@click.option(
    "--term",
    "-t",
    default="long",
    show_default=True,
    help="fetch long/medium/short term tops",
)
@click.pass_context
@ui.echo_feedback("Fetching top artists...", "Artists fetched!")
def topartists(ctx: click.Context, term: str) -> None:
    """Fetches user top artists from Spotify profile."""
    time_range = f"{term}_term"
    artists = operations.get_top_artists(ctx.obj["username"], time_range=time_range)
    ctx.obj["artists"] = artists
    ctx.obj["export"] = artists
    ctx.obj["last"] = "artists"


@main.command()
@click.option(
    "--term",
    "-t",
    default="long",
    show_default=True,
    help="fetch long/medium/short term tops",
)
@click.pass_context
@ui.echo_feedback("Fetching top tracks...", "Tracks fetched!")
def toptracks(ctx: click.Context, term: str) -> None:
    """Fetches user top tracks from Spotify profile."""
    time_range = f"{term}_term"
    tracks = operations.get_top_tracks(ctx.obj["username"], time_range=time_range)
    ctx.obj["tracks"] = tracks
    ctx.obj["export"] = tracks
    ctx.obj["last"] = "tracks"


@main.command()
@click.option("--ask", "-a", is_flag=True, help="ask which albums to save")
@click.pass_context
@ui.echo_feedback("Saving releases to account...", "Releases saved!")
def save(ctx: click.Context, ask: bool) -> None:
    """Saves albums from last command in the Spotify user library."""
    if ask:
        albums_to_save = []
        for album in ctx.obj["albums"]:
            click.echo(
                click.style(album["artists"][0]["name"], fg="magenta", bold=True)
                + click.style(" - ", fg="white")
                + click.style(album["name"], fg="blue", bold=True)
            )
            if click.confirm("Save album", default=True):
                albums_to_save.append(album)
    else:
        albums_to_save = ctx.obj["albums"]
    operations.save_albums(ctx.obj["username"], albums_to_save)


@main.command()
@click.pass_context
def show(ctx: click.Context) -> None:
    """Shows the content of context."""
    for key, parser in PARSERS.items():
        if key in ctx.obj:
            click.echo(parser(ctx.obj[key], print_date=False))


@main.command()
@click.argument("file", type=click.File("w"))
@click.pass_context
@ui.echo_feedback("Writing to file...", "Done!")
def write(ctx: click.Context, file: TextIOWrapper) -> None:
    """Writes results from last command to a file."""
    if file.name.split(".")[-1] == "wiki":
        file.write(PARSERS[ctx.obj["last"]](ctx.obj["export"], print_date=False))
    else:
        file.write(json.dumps(ctx.obj["export"]))


if __name__ == "__main__":
    main()
