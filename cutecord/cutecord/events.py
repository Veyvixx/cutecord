"""
CuteCord Events — friendly event decorators + auto log channel system.

Instead of overriding on_member_join etc., just use the shortcuts:

    @bot.on_join
    async def welcome(member):
        await member.send(f"Hey {member.mention}, welcome!")

    # Or auto-log everything to a channel:
    bot.set_log_channel(channel_id=123456789)

Supported events
----------------
    @bot.on_join            member joins the server
    @bot.on_leave           member leaves / is kicked
    @bot.on_ban             member is banned
    @bot.on_unban           member is unbanned
    @bot.on_nick_change     member changes nickname
    @bot.on_role_add        member gets a role
    @bot.on_role_remove     member loses a role
    @bot.on_delete          message is deleted
    @bot.on_edit            message is edited
    @bot.on_role_create     a new role is created
    @bot.on_role_delete     a role is deleted
    @bot.on_channel_create  a channel is created
    @bot.on_channel_delete  a channel is deleted
    @bot.on_boost           someone boosts the server
    @bot.on_unboost         someone removes their boost
    @bot.on_voice_join      member joins a voice channel
    @bot.on_voice_leave     member leaves a voice channel
    @bot.on_voice_move      member moves between voice channels
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine

import discord

from .embed import Embed


logger = logging.getLogger("cutecord.events")

_CB = Callable[..., Coroutine[Any, Any, Any]]


# ---------------------------------------------------------------------------
# Log channel auto-embed builders
# ---------------------------------------------------------------------------

def _join_embed(member: discord.Member) -> Embed:
    return (
        Embed("📥 Member Joined")
        .color("green")
        .description(f"{member.mention} joined the server.")
        .thumbnail(member.display_avatar.url)
        .field("Account created", member.created_at.strftime("%d %b %Y"), inline=True)
        .field("ID", str(member.id), inline=True)
        .footer(str(member))
        .timestamp()
    )


def _leave_embed(member: discord.Member) -> Embed:
    roles = [r.mention for r in member.roles if r.name != "@everyone"]
    return (
        Embed("📤 Member Left")
        .color("orange")
        .description(f"{member.mention} left the server.")
        .thumbnail(member.display_avatar.url)
        .field("Roles", " ".join(roles) or "None", inline=False)
        .field("ID", str(member.id), inline=True)
        .footer(str(member))
        .timestamp()
    )


def _ban_embed(guild: discord.Guild, user: discord.User) -> Embed:
    return (
        Embed("🔨 Member Banned")
        .color("red")
        .description(f"{user.mention} was banned from **{guild.name}**.")
        .thumbnail(user.display_avatar.url)
        .field("ID", str(user.id), inline=True)
        .footer(str(user))
        .timestamp()
    )


def _unban_embed(guild: discord.Guild, user: discord.User) -> Embed:
    return (
        Embed("🔓 Member Unbanned")
        .color("teal")
        .description(f"{user.mention} was unbanned from **{guild.name}**.")
        .thumbnail(user.display_avatar.url)
        .field("ID", str(user.id), inline=True)
        .footer(str(user))
        .timestamp()
    )


def _nick_embed(member: discord.Member, before: str, after: str) -> Embed:
    return (
        Embed("✏️ Nickname Changed")
        .color("blue")
        .description(f"{member.mention} changed their nickname.")
        .thumbnail(member.display_avatar.url)
        .field("Before", before or "*None*", inline=True)
        .field("After",  after  or "*None*", inline=True)
        .footer(str(member))
        .timestamp()
    )


def _role_add_embed(member: discord.Member, role: discord.Role) -> Embed:
    return (
        Embed("➕ Role Added")
        .color("green")
        .description(f"{member.mention} was given {role.mention}.")
        .footer(str(member))
        .timestamp()
    )


def _role_remove_embed(member: discord.Member, role: discord.Role) -> Embed:
    return (
        Embed("➖ Role Removed")
        .color("orange")
        .description(f"{member.mention} lost {role.mention}.")
        .footer(str(member))
        .timestamp()
    )


def _message_delete_embed(message: discord.Message) -> Embed:
    content = message.content[:1000] or "*[no text content]*"
    return (
        Embed("🗑️ Message Deleted")
        .color("red")
        .description(f"Message by {message.author.mention} deleted in {message.channel.mention}.")
        .field("Content", content, inline=False)
        .field("Author ID", str(message.author.id), inline=True)
        .footer(str(message.author), icon=message.author.display_avatar.url)
        .timestamp()
    )


def _message_edit_embed(before: discord.Message, after: discord.Message) -> Embed:
    b = before.content[:500] or "*[empty]*"
    a = after.content[:500]  or "*[empty]*"
    return (
        Embed("✏️ Message Edited")
        .color("blue")
        .description(f"Message by {after.author.mention} edited in {after.channel.mention}.")
        .field("Before", b, inline=False)
        .field("After",  a, inline=False)
        .footer(str(after.author), icon=after.author.display_avatar.url)
        .timestamp()
    )


def _role_create_embed(role: discord.Role) -> Embed:
    return (
        Embed("🎨 Role Created")
        .color("teal")
        .description(f"New role {role.mention} was created.")
        .field("Color", str(role.color), inline=True)
        .field("Hoisted", "Yes" if role.hoist else "No", inline=True)
        .field("Mentionable", "Yes" if role.mentionable else "No", inline=True)
        .timestamp()
    )


def _role_delete_embed(role: discord.Role) -> Embed:
    return (
        Embed("🗑️ Role Deleted")
        .color("red")
        .description(f"Role **{role.name}** was deleted.")
        .timestamp()
    )


def _channel_create_embed(channel: discord.abc.GuildChannel) -> Embed:
    return (
        Embed("📢 Channel Created")
        .color("green")
        .description(f"New channel {channel.mention} was created.")
        .field("Type", str(channel.type).replace("_", " ").title(), inline=True)
        .timestamp()
    )


def _channel_delete_embed(channel: discord.abc.GuildChannel) -> Embed:
    return (
        Embed("🗑️ Channel Deleted")
        .color("red")
        .description(f"Channel **#{channel.name}** was deleted.")
        .field("Type", str(channel.type).replace("_", " ").title(), inline=True)
        .timestamp()
    )


def _boost_embed(member: discord.Member) -> Embed:
    count = member.guild.premium_subscription_count
    return (
        Embed("💎 Server Boosted!")
        .color("fuchsia")
        .description(f"{member.mention} just boosted the server! 🎉")
        .field("Total Boosts", str(count), inline=True)
        .field("Boost Tier", str(member.guild.premium_tier), inline=True)
        .thumbnail(member.display_avatar.url)
        .footer(str(member))
        .timestamp()
    )


def _unboost_embed(member: discord.Member) -> Embed:
    count = member.guild.premium_subscription_count
    return (
        Embed("💔 Boost Removed")
        .color("purple")
        .description(f"{member.mention} removed their boost.")
        .field("Total Boosts", str(count), inline=True)
        .footer(str(member))
        .timestamp()
    )


def _voice_join_embed(member: discord.Member, channel: discord.VoiceChannel) -> Embed:
    return (
        Embed("🔊 Joined Voice")
        .color("green")
        .description(f"{member.mention} joined **{channel.name}**.")
        .footer(str(member), icon=member.display_avatar.url)
        .timestamp()
    )


def _voice_leave_embed(member: discord.Member, channel: discord.VoiceChannel) -> Embed:
    return (
        Embed("🔇 Left Voice")
        .color("orange")
        .description(f"{member.mention} left **{channel.name}**.")
        .footer(str(member), icon=member.display_avatar.url)
        .timestamp()
    )


def _voice_move_embed(member: discord.Member, before: discord.VoiceChannel, after: discord.VoiceChannel) -> Embed:
    return (
        Embed("🔀 Moved Voice Channel")
        .color("blue")
        .description(f"{member.mention} moved voice channels.")
        .field("From", before.name, inline=True)
        .field("To",   after.name,  inline=True)
        .footer(str(member), icon=member.display_avatar.url)
        .timestamp()
    )


# ---------------------------------------------------------------------------
# Event mixin
# ---------------------------------------------------------------------------

class _EventMixin:
    """
    Mixed into :class:`~cutecord.Bot` to provide friendly event decorators
    and the ``set_log_channel`` auto-logging system.
    """

    # ── internal state ───────────────────────────────────────────────────
    _log_channel_id: int | None
    _log_events: set[str]
    _cute_event_callbacks: dict[str, list[_CB]]

    def _init_events(self) -> None:
        if not hasattr(self, "_log_channel_id"):
            self._log_channel_id = None
        if not hasattr(self, "_log_events"):
            self._log_events = set()
        if not hasattr(self, "_cute_event_callbacks"):
            self._cute_event_callbacks = {}

    # ── log channel ──────────────────────────────────────────────────────

    def set_log_channel(
        self,
        channel_id: int,
        events: list[str] | None = None,
    ) -> None:
        """
        Enable automatic event logging to a Discord channel.

        Parameters
        ----------
        channel_id:
            The ID of the text channel to send log embeds to.
        events:
            Which events to log.  Defaults to all supported events.
            Choices: ``"join"``, ``"leave"``, ``"ban"``, ``"unban"``,
            ``"nick_change"``, ``"role_add"``, ``"role_remove"``,
            ``"delete"``, ``"edit"``, ``"role_create"``, ``"role_delete"``,
            ``"channel_create"``, ``"channel_delete"``, ``"boost"``,
            ``"unboost"``, ``"voice_join"``, ``"voice_leave"``, ``"voice_move"``.

        Example
        -------
            bot.set_log_channel(1234567890)              # log everything
            bot.set_log_channel(1234567890, events=["ban", "unban", "join"])
        """
        self._init_events()
        self._log_channel_id = channel_id
        self._log_events = set(events) if events is not None else {
            "join", "leave", "ban", "unban",
            "nick_change", "role_add", "role_remove",
            "delete", "edit",
            "role_create", "role_delete",
            "channel_create", "channel_delete",
            "boost", "unboost",
            "voice_join", "voice_leave", "voice_move",
        }
        logger.info("Log channel set to %s, events: %s", channel_id, self._log_events)

    async def _send_log(self, embed: Embed) -> None:
        """Send *embed* to the configured log channel (silently ignores errors)."""
        if not self._log_channel_id:
            return
        channel = self.get_channel(self._log_channel_id)  # type: ignore[attr-defined]
        if channel and hasattr(channel, "send"):
            try:
                await channel.send(embed=embed.build())
            except discord.HTTPException as exc:
                logger.warning("Could not send log embed: %s", exc)

    async def _fire(self, event_name: str, *args: Any) -> None:
        """Run all registered callbacks for *event_name*."""
        self._init_events()
        for cb in self._cute_event_callbacks.get(event_name, []):
            try:
                await cb(*args)
            except Exception as exc:
                logger.error("Error in %s callback: %s", event_name, exc, exc_info=True)

    def _register(self, event_name: str, coro: _CB) -> _CB:
        self._init_events()
        self._cute_event_callbacks.setdefault(event_name, []).append(coro)
        return coro

    # ── decorator helpers ────────────────────────────────────────────────

    def on_join(self, coro: _CB) -> _CB:
        """
        Register a callback that fires when a member joins.

        Callback signature: ``async def callback(member: discord.Member)``

        Example
        -------
            @bot.on_join
            async def greet(member):
                await member.send(f"Welcome, {member.display_name}!")
        """
        return self._register("join", coro)

    def on_leave(self, coro: _CB) -> _CB:
        """Fires when a member leaves or is kicked. ``(member)``"""
        return self._register("leave", coro)

    def on_ban(self, coro: _CB) -> _CB:
        """Fires when a member is banned. ``(guild, user)``"""
        return self._register("ban", coro)

    def on_unban(self, coro: _CB) -> _CB:
        """Fires when a member is unbanned. ``(guild, user)``"""
        return self._register("unban", coro)

    def on_nick_change(self, coro: _CB) -> _CB:
        """Fires when a member changes their nickname. ``(member, before_nick, after_nick)``"""
        return self._register("nick_change", coro)

    def on_role_add(self, coro: _CB) -> _CB:
        """Fires when a member gains a role. ``(member, role)``"""
        return self._register("role_add", coro)

    def on_role_remove(self, coro: _CB) -> _CB:
        """Fires when a member loses a role. ``(member, role)``"""
        return self._register("role_remove", coro)

    def on_delete(self, coro: _CB) -> _CB:
        """Fires when a message is deleted. ``(message)``"""
        return self._register("delete", coro)

    def on_edit(self, coro: _CB) -> _CB:
        """Fires when a message is edited. ``(before, after)``"""
        return self._register("edit", coro)

    def on_role_create(self, coro: _CB) -> _CB:
        """Fires when a new role is created. ``(role)``"""
        return self._register("role_create", coro)

    def on_role_delete(self, coro: _CB) -> _CB:
        """Fires when a role is deleted. ``(role)``"""
        return self._register("role_delete", coro)

    def on_channel_create(self, coro: _CB) -> _CB:
        """Fires when a channel is created. ``(channel)``"""
        return self._register("channel_create", coro)

    def on_channel_delete(self, coro: _CB) -> _CB:
        """Fires when a channel is deleted. ``(channel)``"""
        return self._register("channel_delete", coro)

    def on_boost(self, coro: _CB) -> _CB:
        """Fires when a member boosts the server. ``(member)``"""
        return self._register("boost", coro)

    def on_unboost(self, coro: _CB) -> _CB:
        """Fires when a member removes their boost. ``(member)``"""
        return self._register("unboost", coro)

    def on_voice_join(self, coro: _CB) -> _CB:
        """Fires when a member joins a voice channel. ``(member, channel)``"""
        return self._register("voice_join", coro)

    def on_voice_leave(self, coro: _CB) -> _CB:
        """Fires when a member leaves a voice channel. ``(member, channel)``"""
        return self._register("voice_leave", coro)

    def on_voice_move(self, coro: _CB) -> _CB:
        """Fires when a member moves between voice channels. ``(member, before_channel, after_channel)``"""
        return self._register("voice_move", coro)

    # ── discord.py event handlers (called internally) ────────────────────

    async def on_member_join(self, member: discord.Member) -> None:
        self._init_events()
        if "join" in self._log_events:
            await self._send_log(_join_embed(member))
        await self._fire("join", member)

    async def on_member_remove(self, member: discord.Member) -> None:
        self._init_events()
        if "leave" in self._log_events:
            await self._send_log(_leave_embed(member))
        await self._fire("leave", member)

    async def on_member_ban(self, guild: discord.Guild, user: discord.User) -> None:
        self._init_events()
        if "ban" in self._log_events:
            await self._send_log(_ban_embed(guild, user))
        await self._fire("ban", guild, user)

    async def on_member_unban(self, guild: discord.Guild, user: discord.User) -> None:
        self._init_events()
        if "unban" in self._log_events:
            await self._send_log(_unban_embed(guild, user))
        await self._fire("unban", guild, user)

    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        self._init_events()

        # Nickname change
        if before.nick != after.nick:
            if "nick_change" in self._log_events:
                await self._send_log(_nick_embed(after, before.nick or "", after.nick or ""))
            await self._fire("nick_change", after, before.nick or "", after.nick or "")

        # Roles changed
        added_roles   = [r for r in after.roles  if r not in before.roles]
        removed_roles = [r for r in before.roles if r not in after.roles]

        for role in added_roles:
            if "role_add" in self._log_events:
                await self._send_log(_role_add_embed(after, role))
            await self._fire("role_add", after, role)

        for role in removed_roles:
            if "role_remove" in self._log_events:
                await self._send_log(_role_remove_embed(after, role))
            await self._fire("role_remove", after, role)

        # Boost / unboost detection
        before_boost = before.premium_since
        after_boost  = after.premium_since
        if before_boost is None and after_boost is not None:
            if "boost" in self._log_events:
                await self._send_log(_boost_embed(after))
            await self._fire("boost", after)
        elif before_boost is not None and after_boost is None:
            if "unboost" in self._log_events:
                await self._send_log(_unboost_embed(after))
            await self._fire("unboost", after)

    async def on_message_delete(self, message: discord.Message) -> None:
        self._init_events()
        if message.author.bot:
            return
        if "delete" in self._log_events:
            await self._send_log(_message_delete_embed(message))
        await self._fire("delete", message)

    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        self._init_events()
        if after.author.bot or before.content == after.content:
            return
        if "edit" in self._log_events:
            await self._send_log(_message_edit_embed(before, after))
        await self._fire("edit", before, after)

    async def on_guild_role_create(self, role: discord.Role) -> None:
        self._init_events()
        if "role_create" in self._log_events:
            await self._send_log(_role_create_embed(role))
        await self._fire("role_create", role)

    async def on_guild_role_delete(self, role: discord.Role) -> None:
        self._init_events()
        if "role_delete" in self._log_events:
            await self._send_log(_role_delete_embed(role))
        await self._fire("role_delete", role)

    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        self._init_events()
        if "channel_create" in self._log_events:
            await self._send_log(_channel_create_embed(channel))
        await self._fire("channel_create", channel)

    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        self._init_events()
        if "channel_delete" in self._log_events:
            await self._send_log(_channel_delete_embed(channel))
        await self._fire("channel_delete", channel)

    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        self._init_events()
        b_chan = before.channel
        a_chan = after.channel

        if b_chan is None and a_chan is not None:
            if "voice_join" in self._log_events:
                await self._send_log(_voice_join_embed(member, a_chan))  # type: ignore[arg-type]
            await self._fire("voice_join", member, a_chan)

        elif b_chan is not None and a_chan is None:
            if "voice_leave" in self._log_events:
                await self._send_log(_voice_leave_embed(member, b_chan))  # type: ignore[arg-type]
            await self._fire("voice_leave", member, b_chan)

        elif b_chan is not None and a_chan is not None and b_chan != a_chan:
            if "voice_move" in self._log_events:
                await self._send_log(_voice_move_embed(member, b_chan, a_chan))  # type: ignore[arg-type]
            await self._fire("voice_move", member, b_chan, a_chan)
