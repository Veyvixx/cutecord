"""
CuteCord Checks — readable permission checks for slash commands.

Usage
-----
    from cutecord.checks import is_admin, has_role, is_owner, in_channel

    @bot.slash_command()
    @is_admin()
    async def nuke(ctx): ...

    @bot.slash_command()
    @has_role("Moderator")
    async def warn(ctx, member): ...

    @bot.slash_command()
    @is_owner()
    async def reload(ctx): ...

    @bot.slash_command()
    @in_channel(123456789)
    async def daily(ctx): ...

All checks raise :class:`discord.ext.commands.CheckFailure` on failure,
which CuteCord's error handler catches and turns into a red embed automatically.
"""

from __future__ import annotations

import discord
from discord.ext import commands


def is_admin():
    """Require the invoker to have the Administrator permission."""
    async def predicate(ctx: discord.ApplicationContext) -> bool:
        if not isinstance(ctx.author, discord.Member):
            raise commands.NoPrivateMessage()
        if ctx.author.guild_permissions.administrator:
            return True
        raise commands.CheckFailure("You need the **Administrator** permission to use this.")
    return commands.check(predicate)


def is_mod():
    """Require the invoker to have Manage Messages or higher."""
    async def predicate(ctx: discord.ApplicationContext) -> bool:
        if not isinstance(ctx.author, discord.Member):
            raise commands.NoPrivateMessage()
        perms = ctx.author.guild_permissions
        if perms.manage_messages or perms.administrator:
            return True
        raise commands.CheckFailure("You need the **Manage Messages** permission to use this.")
    return commands.check(predicate)


def is_owner():
    """Restrict the command to the bot's owner (from the Developer Portal)."""
    async def predicate(ctx: discord.ApplicationContext) -> bool:
        app = await ctx.bot.application_info()
        if ctx.author.id == app.owner.id:
            return True
        raise commands.NotOwner()
    return commands.check(predicate)


def has_role(*role_names_or_ids: str | int):
    """
    Require the invoker to have at least one of the given roles.

    Accepts role names (str) or role IDs (int).

    Example
    -------
        @has_role("Moderator", "Admin")
        @has_role(987654321)
    """
    async def predicate(ctx: discord.ApplicationContext) -> bool:
        if not isinstance(ctx.author, discord.Member):
            raise commands.NoPrivateMessage()
        member_role_names = {r.name for r in ctx.author.roles}
        member_role_ids   = {r.id   for r in ctx.author.roles}
        for item in role_names_or_ids:
            if isinstance(item, str) and item in member_role_names:
                return True
            if isinstance(item, int) and item in member_role_ids:
                return True
        names = ", ".join(f"**{r}**" for r in role_names_or_ids)
        raise commands.CheckFailure(f"You need one of these roles to use this: {names}.")
    return commands.check(predicate)


def in_channel(*channel_ids: int):
    """
    Restrict the command to specific channels.

    Example
    -------
        @in_channel(123456789, 987654321)
    """
    async def predicate(ctx: discord.ApplicationContext) -> bool:
        if ctx.channel_id in channel_ids:
            return True
        raise commands.CheckFailure("This command can't be used in this channel.")
    return commands.check(predicate)


def in_guild(*guild_ids: int):
    """Restrict the command to specific guilds (servers)."""
    async def predicate(ctx: discord.ApplicationContext) -> bool:
        if ctx.guild_id in guild_ids:
            return True
        raise commands.CheckFailure("This command isn't available in this server.")
    return commands.check(predicate)


def bot_has_perms(**perms: bool):
    """
    Require the bot to have specific permissions before running the command.

    Example
    -------
        @bot_has_perms(manage_messages=True, embed_links=True)
    """
    async def predicate(ctx: discord.ApplicationContext) -> bool:
        if not ctx.guild:
            raise commands.NoPrivateMessage()
        bot_member = ctx.guild.me
        bot_perms = bot_member.guild_permissions
        missing = [p for p, v in perms.items() if not getattr(bot_perms, p, False)]
        if not missing:
            return True
        raise commands.BotMissingPermissions(missing)
    return commands.check(predicate)
