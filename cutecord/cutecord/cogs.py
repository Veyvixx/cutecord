"""
CuteCord Cogs — dead-simple cog (extension) management.

Features
--------
  - bot.load_cogs("cogs/")    — load every .py file in a folder automatically
  - bot.reload_cogs("cogs/")  — hot-reload all cogs (great during development)
  - bot.unload_cogs("cogs/")  — unload all cogs from a folder
  - Cog base class            — just subclass it; setup() is written for you

Folder convention
-----------------
    cogs/
    ├── fun.py        ← defines class Fun(Cog): ...
    ├── moderation.py ← defines class Moderation(Cog): ...
    └── welcome.py    ← defines class Welcome(Cog): ...

    # bot.py
    from cutecord import Bot
    bot = Bot()
    bot.load_cogs("cogs/")   # loads fun, moderation, welcome automatically
    bot.run()

Any file that starts with _ is skipped (e.g. __init__.py, _helpers.py).

Cog base class
--------------
    # cogs/fun.py
    from cutecord import Cog
    import discord

    class Fun(Cog):
        @discord.slash_command()
        async def roll(self, ctx):
            import random
            await ctx.respond(f"🎲 You rolled a {random.randint(1, 6)}!")

    # No setup() needed — Cog handles it.
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import sys
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    pass

logger = logging.getLogger("cutecord.cogs")


# ---------------------------------------------------------------------------
# Cog base class
# ---------------------------------------------------------------------------

class Cog(commands.Cog):
    """
    Base class for CuteCord cogs.

    Subclass this instead of ``discord.ext.commands.Cog``.
    A ``setup()`` function is automatically provided — you don't need to
    write one in your cog file.

    Example
    -------
        # cogs/fun.py
        from cutecord import Cog
        import discord

        class Fun(Cog):
            description = "Fun commands"

            @discord.slash_command(description="Roll a dice")
            async def roll(self, ctx):
                import random
                await ctx.respond(f"You rolled {random.randint(1, 6)}!")
    """

    # Friendly description shown in help embeds etc.
    description: str = ""


def _make_setup(cog_class: type[Cog]):
    """Return a ``setup(bot)`` function that adds *cog_class* to the bot."""
    async def setup(bot: commands.Bot) -> None:
        await bot.add_cog(cog_class(bot))

    return setup


# ---------------------------------------------------------------------------
# Module loading helpers
# ---------------------------------------------------------------------------

def _module_name_from_path(path: Path, root: Path) -> str:
    """Convert a file path to a dotted module name relative to *root*."""
    relative = path.relative_to(root.parent)
    parts = list(relative.with_suffix("").parts)
    return ".".join(parts)


def _discover_cog_files(folder: Path) -> list[Path]:
    """Return all .py files in *folder* (non-recursive) that don't start with _."""
    return sorted(
        p for p in folder.iterdir()
        if p.suffix == ".py" and not p.stem.startswith("_")
    )


def _extension_name(path: Path, root: Path) -> str:
    """
    Return the extension name string that discord.py uses for load_extension.
    This is a dotted module path relative to ``sys.path``.
    """
    # Make sure the root's *parent* is on sys.path so imports work
    parent = str(root.parent.resolve())
    if parent not in sys.path:
        sys.path.insert(0, parent)

    rel = path.relative_to(root.parent)
    return str(rel.with_suffix("")).replace("/", ".").replace("\\", ".")


# ---------------------------------------------------------------------------
# Bot mixin — injected into cutecord.Bot
# ---------------------------------------------------------------------------

class _CogLoaderMixin:
    """
    Mixed into :class:`~cutecord.Bot` to provide ``load_cogs``,
    ``reload_cogs``, and ``unload_cogs``.
    """

    # Tracks which extension names came from which folder path
    _cute_cog_folders: dict[str, list[str]]

    def _ensure_cog_tracker(self) -> None:
        if not hasattr(self, "_cute_cog_folders"):
            self._cute_cog_folders = {}

    async def load_cogs(self, folder: str | Path) -> list[str]:
        """
        Load every cog file found in *folder*.

        Parameters
        ----------
        folder:
            Path to a directory containing cog ``.py`` files.

        Returns
        -------
        list[str]
            The extension names that were successfully loaded.

        Example
        -------
            await bot.load_cogs("cogs/")
        """
        self._ensure_cog_tracker()
        root = Path(folder).resolve()
        if not root.is_dir():
            raise NotADirectoryError(f"Cog folder not found: {root}")

        loaded: list[str] = []
        for path in _discover_cog_files(root):
            ext = _extension_name(path, root)
            try:
                await self.load_extension(ext)  # type: ignore[attr-defined]
                loaded.append(ext)
                logger.info("Loaded cog: %s", ext)
            except Exception as exc:
                logger.error("Failed to load cog %s: %s", ext, exc, exc_info=True)

        self._cute_cog_folders[str(root)] = loaded
        if loaded:
            print(f"✨ Loaded {len(loaded)} cog(s) from {root.name}/: {', '.join(p.split('.')[-1] for p in loaded)}")
        else:
            print(f"⚠️  No cogs found in {root}/")
        return loaded

    async def reload_cogs(self, folder: str | Path) -> list[str]:
        """
        Hot-reload all cogs that were loaded from *folder*.

        If a cog was not previously loaded it will be loaded fresh.

        Parameters
        ----------
        folder:
            The same folder path you passed to :meth:`load_cogs`.

        Returns
        -------
        list[str]
            The extension names that were successfully reloaded.

        Example
        -------
            await bot.reload_cogs("cogs/")
        """
        self._ensure_cog_tracker()
        root = Path(folder).resolve()
        if not root.is_dir():
            raise NotADirectoryError(f"Cog folder not found: {root}")

        # Make sure parent is on path
        parent = str(root.parent)
        if parent not in sys.path:
            sys.path.insert(0, parent)

        reloaded: list[str] = []
        for path in _discover_cog_files(root):
            ext = _extension_name(path, root)
            try:
                if ext in self.extensions:  # type: ignore[attr-defined]
                    await self.reload_extension(ext)  # type: ignore[attr-defined]
                    reloaded.append(ext)
                    logger.info("Reloaded cog: %s", ext)
                else:
                    await self.load_extension(ext)  # type: ignore[attr-defined]
                    reloaded.append(ext)
                    logger.info("Loaded new cog: %s", ext)
            except Exception as exc:
                logger.error("Failed to reload cog %s: %s", ext, exc, exc_info=True)

        self._cute_cog_folders[str(root)] = reloaded
        print(f"🔄 Reloaded {len(reloaded)} cog(s) from {root.name}/")
        return reloaded

    async def unload_cogs(self, folder: str | Path) -> list[str]:
        """
        Unload all cogs that were loaded from *folder*.

        Parameters
        ----------
        folder:
            The same folder path you passed to :meth:`load_cogs`.

        Returns
        -------
        list[str]
            The extension names that were successfully unloaded.

        Example
        -------
            await bot.unload_cogs("cogs/")
        """
        self._ensure_cog_tracker()
        root = str(Path(folder).resolve())
        extensions = self._cute_cog_folders.get(root, [])

        unloaded: list[str] = []
        for ext in extensions:
            try:
                await self.unload_extension(ext)  # type: ignore[attr-defined]
                unloaded.append(ext)
                logger.info("Unloaded cog: %s", ext)
            except Exception as exc:
                logger.error("Failed to unload cog %s: %s", ext, exc, exc_info=True)

        self._cute_cog_folders.pop(root, None)
        print(f"🗑️  Unloaded {len(unloaded)} cog(s) from {Path(root).name}/")
        return unloaded
