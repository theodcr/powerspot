"""
Helpers for CLI appearence and UI
"""

from functools import update_wrapper

import click

GREET = """
    ____                          _____             __
   / __ \____ _      _____  _____/ ___/____  ____  / /_
  / /_/ / __ \ | /| / / _ \/ ___/\__ \/ __ \/ __ \/ __/
 / ____/ /_/ / |/ |/ /  __/ /   ___/ / /_/ / /_/ / /_
/_/    \____/|__/|__/\___/_/   /____/ .___/\____/\__/
                                   /_/
"""


def echo_feedback(before, after):
    """Decorators to echo messages before and after calling a function"""
    def pass_obj(function):
        @click.pass_context
        def wrapper(ctx, *args, **kwargs):
            click.echo(click.style(before, fg='cyan'))
            ctx.invoke(function, *args, **kwargs)
            click.echo(click.style(f"{after}\n", fg='blue', bold=True))

        return update_wrapper(wrapper, function)

    return pass_obj
