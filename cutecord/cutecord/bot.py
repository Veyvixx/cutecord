"""
CuteBot — a discord.py Bot subclass with auto dotenv loading,
and a few quality-of-life extras.
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Any

import discord
from discord.ext import commands
from dotenv import load_dotenv

from .cogs import _CogLoaderMixin
from .context import CuteContext
from .events import _EventMixin
from .errors import _ErrorHandlerMixin


logger = logging.getLogger("cutecord")


def _find_dotenv(start: Path | None = None) -> Path | None:
    """Walk up from start looking for a .env file."""
    current = (start or Path.cwd()).resolve()
    for directory in [current, *current.parents]:
        candidate = directory / ".env"
        if candidate.is_file():
            return candidate
    return None


class Bot(_CogLoaderMixin, _EventMixin, _ErrorHandlerMixin, commands.Bot):
    """
    A discord.py Bot that automatically loads your .env file.

    Parameters
    ----------
    token_var:
        Name of the environment variable that holds your bot token.
        Defaults to "DISCORD_TOKEN".
    dotenv_path:
        Explicit path to a .env file.  When ``None`` (default) CuteCord
        searches upward from the current working directory.
    log_level:
        Python logging level for the ``cutecord`` logger.
        Set to ``None`` to disable automatic logging setup.
    **kwargs:
        Forwarded verbatim to :class:`discord.ext.commands.Bot`.

    Example
    -------
    >>> bot = Bot()
    >>> bot.run()          # token read from DISCORD_TOKEN in .env
    >>> bot.run("TOKEN")   # or pass it directly
    """

    def __init__(
        self,
        *,
        token_var: str = "DISCORD_TOKEN",
        dotenv_path: str | Path | None = None,
        log_level: int | None = logging.INFO,
        command_prefix: str | list[str] = "!",
        intents: discord.Intents | None = None,
        **kwargs: Any,
    ) -> None:
        self._token_var = token_var
        self._dotenv_loaded = False

        # --- auto dotenv -------------------------------------------------
        env_path = Path(dotenv_path) if dotenv_path else _find_dotenv()
        if env_path:
            load_dotenv(dotenv_path=env_path, override=False)
            self._dotenv_loaded = True
            logger.debug("Loaded .env from %s", env_path)
        else:
            logger.debug("No .env file found; skipping dotenv load")

        # --- logging setup -----------------------------------------------
        if log_level is not None:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
            )
            logging.getLogger("cutecord").setLevel(log_level)
            logging.getLogger("cutecord").addHandler(handler)

        # --- intents default ---------------------------------------------
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True

        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Use CuteContext for every slash command
    # ------------------------------------------------------------------

    async def get_application_context(
        self,
        interaction: discord.Interaction,
        cls: type = None,  # type: ignore[assignment]
    ) -> CuteContext:
        return await super().get_application_context(  # type: ignore[return-value]
            interaction, cls=cls or CuteContext
        )

    # ------------------------------------------------------------------
    # run() override
    # ------------------------------------------------------------------

    def run(self, token: str | None = None, **kwargs: Any) -> None:  # type: ignore[override]
        """
        Start the bot.

        If *token* is omitted CuteCord reads ``self._token_var`` from
        the environment (populated by the auto dotenv load).

        Parameters
        ----------
        token:
            Bot token.  Omit to use the environment variable.
        **kwargs:
            Forwarded to :meth:`discord.ext.commands.Bot.run`.
        """
        resolved = token or os.environ.get(self._token_var)
        if not resolved:
            raise RuntimeError(
                f"No bot token found.  Set {self._token_var!r} in your .env file "
                "or pass it directly to bot.run()."
            )
        super().run(resolved, **kwargs)

    # ------------------------------------------------------------------
    # Convenience: async on_ready banner
    # ------------------------------------------------------------------

    async def on_ready(self) -> None:  # type: ignore[override]
        assert self.user is not None
        logger.info("Logged in as %s (id=%s)", self.user, self.user.id)
        print(f"✨ CuteCord bot ready — logged in as {self.user} ({self.user.id})")
