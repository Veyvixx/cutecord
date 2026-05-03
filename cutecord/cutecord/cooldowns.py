"""
CuteCord Cooldowns — dead-simple cooldown decorators for slash commands.

Instead of writing discord.py's full cooldown syntax, just use:

    @bot.slash_command()
    @cooldown(5)                       # 5 seconds, per user
    @cooldown(30, per="channel")       # 30 seconds, per channel
    @cooldown(60, per="guild")         # 60 seconds, per guild
    async def my_command(ctx):
        ...

Or use the named shortcuts:

    @once_per(10)     # alias for cooldown(10)
    @slow(5)          # alias for cooldown(5)

The error message is handled automatically by CuteCord's error handler.
"""

from __future__ import annotations

from typing import Literal

import discord
from discord.ext import commands


_BucketMap = {
    "user":    commands.BucketType.user,
    "member":  commands.BucketType.member,
    "guild":   commands.BucketType.guild,
    "channel": commands.BucketType.channel,
    "global":  commands.BucketType.default,
}


def cooldown(
    seconds: float,
    *,
    rate: int = 1,
    per: Literal["user", "member", "guild", "channel", "global"] = "user",
):
    """
    Add a cooldown to a slash command.

    Parameters
    ----------
    seconds:
        How long to wait between uses (in seconds).
    rate:
        How many times the command can be used before the cooldown kicks in.
        Default: 1.
    per:
        Who the cooldown applies to: ``"user"`` (default), ``"member"``,
        ``"guild"``, ``"channel"``, or ``"global"``.

    Example
    -------
        @bot.slash_command()
        @cooldown(10)                      # once every 10s per user
        @cooldown(30, rate=3, per="guild") # 3 times per 30s per guild
        async def my_cmd(ctx):
            await ctx.success("Done!")
    """
    bucket = _BucketMap.get(per, commands.BucketType.user)
    return commands.cooldown(rate=rate, per=seconds, type=bucket)


def once_per(seconds: float, *, per: str = "user"):
    """Alias for :func:`cooldown` — reads more naturally in code."""
    return cooldown(seconds, per=per)  # type: ignore[arg-type]


def slow(seconds: float):
    """Rate-limit a command per user with a single argument."""
    return cooldown(seconds)
