"""
CuteCord Errors — global error handler mixin.

Automatically catches slash command errors and sends a clean red embed.
Supports custom error maps for your own exceptions.

Usage
-----
    # Default handler (automatic — just use Bot)
    bot = Bot()

    # Add a custom exception → message mapping:
    bot.map_error(MyCustomError, "That's a custom error: {error}")

    # Fully override the handler:
    @bot.on_command_error
    async def handle(ctx, error):
        await ctx.error(str(error))
"""

from __future__ import annotations

import logging
import traceback
from typing import Any

import discord
from discord.ext import commands
from discord import ApplicationCommandError


logger = logging.getLogger("cutecord.errors")


class _ErrorHandlerMixin:
    """
    Mixed into :class:`~cutecord.Bot` to provide automatic slash command
    error handling with styled embeds.
    """

    _cute_error_map: dict[type[Exception], str]
    _cute_error_override: Any

    def _init_errors(self) -> None:
        if not hasattr(self, "_cute_error_map"):
            self._cute_error_map = {}
        if not hasattr(self, "_cute_error_override"):
            self._cute_error_override = None

    def map_error(self, exc_type: type[Exception], message: str) -> None:
        """
        Map an exception type to a user-facing error message.

        Use ``{error}`` as a placeholder for the exception's string value.

        Parameters
        ----------
        exc_type:
            The exception class to catch.
        message:
            The message shown to the user.  Supports ``{error}`` placeholder.

        Example
        -------
            bot.map_error(ValueError, "Invalid value: {error}")
            bot.map_error(PermissionError, "You don't have permission to do that.")
        """
        self._init_errors()
        self._cute_error_map[exc_type] = message

    def on_command_error(self, coro: Any) -> Any:
        """
        Override the default error handler with your own async function.

        Callback signature: ``async def handler(ctx, error) -> None``

        Example
        -------
            @bot.on_command_error
            async def my_handler(ctx, error):
                await ctx.error(f"Something went wrong: {error}")
        """
        self._init_errors()
        self._cute_error_override = coro
        return coro

    async def on_application_command_error(
        self,
        ctx: discord.ApplicationContext,
        error: ApplicationCommandError,
    ) -> None:
        self._init_errors()

        # Custom override
        if self._cute_error_override:
            try:
                await self._cute_error_override(ctx, error)
            except Exception as e:
                logger.error("Error in custom error handler: %s", e, exc_info=True)
            return

        # Unwrap CheckFailure / CommandInvokeError etc.
        cause = getattr(error, "original", error)

        # Check custom error map
        for exc_type, msg_template in self._cute_error_map.items():
            if isinstance(cause, exc_type):
                msg = msg_template.replace("{error}", str(cause))
                await _safe_error(ctx, msg)
                return

        # Built-in discord.py errors
        if isinstance(cause, commands.MissingPermissions):
            perms = ", ".join(cause.missing_permissions)
            await _safe_error(ctx, f"You need the **{perms}** permission(s) to use this.")
            return

        if isinstance(cause, commands.BotMissingPermissions):
            perms = ", ".join(cause.missing_permissions)
            await _safe_error(ctx, f"I need the **{perms}** permission(s) to do that.")
            return

        if isinstance(cause, commands.MissingRequiredArgument):
            await _safe_error(ctx, f"Missing required argument: `{cause.param.name}`.")
            return

        if isinstance(cause, commands.CommandOnCooldown):
            await _safe_error(
                ctx,
                f"This command is on cooldown. Try again in **{cause.retry_after:.1f}s**.",
            )
            return

        if isinstance(cause, commands.NotOwner):
            await _safe_error(ctx, "Only the bot owner can use this command.")
            return

        if isinstance(cause, commands.NoPrivateMessage):
            await _safe_error(ctx, "This command can only be used in a server.")
            return

        if isinstance(cause, commands.PrivateMessageOnly):
            await _safe_error(ctx, "This command can only be used in DMs.")
            return

        if isinstance(cause, discord.Forbidden):
            await _safe_error(ctx, "I don't have permission to do that.")
            return

        if isinstance(cause, discord.NotFound):
            await _safe_error(ctx, "That resource was not found.")
            return

        # Unknown error — log it, send a generic message
        logger.error(
            "Unhandled command error in %s: %s",
            ctx.command,
            cause,
            exc_info=cause,
        )
        await _safe_error(
            ctx,
            "An unexpected error occurred. Please try again later.",
            title="❌ Internal Error",
        )


async def _safe_error(
    ctx: discord.ApplicationContext,
    message: str,
    title: str = "❌ Error",
) -> None:
    """Send an error embed, handling the case where the interaction was already responded to."""
    from .embed import Embed

    embed = Embed(title).color("red").description(message)
    try:
        if ctx.response.is_done():
            await ctx.followup.send(embed=embed.build(), ephemeral=True)
        else:
            await ctx.respond(embed=embed.build(), ephemeral=True)
    except discord.HTTPException:
        pass
