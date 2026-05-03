"""
CuteCord Utils — helpers for reading local files into bot messages.

read_file()       — sync, returns str
read_file_async() — async, returns str (uses aiofiles when available)
attach()          — wrap a file path into a discord.File for sending
attach_many()     — wrap multiple paths at once
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import discord


PathLike = Union[str, Path]


# ---------------------------------------------------------------------------
# Text file readers
# ---------------------------------------------------------------------------

def read_file(path: PathLike, encoding: str = "utf-8") -> str:
    """
    Read a text file and return its contents as a string.

    Parameters
    ----------
    path:
        Path to the file.
    encoding:
        File encoding.  Defaults to ``"utf-8"``.

    Example
    -------
        rules = read_file("content/rules.md")
        await ctx.respond(rules[:2000])
    """
    return Path(path).read_text(encoding=encoding)


async def read_file_async(path: PathLike, encoding: str = "utf-8") -> str:
    """
    Async version of :func:`read_file`.

    Uses *aiofiles* if installed, otherwise falls back to a thread executor.

    Example
    -------
        text = await read_file_async("content/welcome.md")
        await ctx.respond(text[:2000])
    """
    try:
        import aiofiles  # type: ignore[import-untyped]

        async with aiofiles.open(path, mode="r", encoding=encoding) as fh:
            return await fh.read()
    except ImportError:
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: Path(path).read_text(encoding=encoding))


# ---------------------------------------------------------------------------
# File attachment helpers
# ---------------------------------------------------------------------------

def attach(
    path: PathLike,
    *,
    filename: str | None = None,
    description: str | None = None,
    spoiler: bool = False,
) -> discord.File:
    """
    Wrap a local file path into a :class:`discord.File` ready for sending.

    Parameters
    ----------
    path:
        Path to the file.
    filename:
        Override the filename shown in Discord.  Defaults to the file's actual name.
    description:
        Alt-text / accessibility description (images only).
    spoiler:
        Mark the attachment as a spoiler.

    Example
    -------
        await ctx.respond("Here's the log:", file=attach("logs/latest.txt"))
    """
    p = Path(path)
    return discord.File(
        p,
        filename=filename or p.name,
        description=description,
        spoiler=spoiler,
    )


def attach_many(*paths: PathLike) -> list[discord.File]:
    """
    Wrap multiple file paths into a list of :class:`discord.File` objects.

    Parameters
    ----------
    *paths:
        Any number of file paths.

    Example
    -------
        await ctx.respond("Check these out:", files=attach_many("img1.png", "img2.png"))
    """
    return [attach(p) for p in paths]
