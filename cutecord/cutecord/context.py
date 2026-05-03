"""
CuteCord CuteContext — a custom ApplicationContext with one-liner response shortcuts.

Instead of building an embed every time, just call:

    await ctx.success("Done!")
    await ctx.error("Something went wrong.")
    await ctx.info("Here's what I found…")
    await ctx.warn("Are you sure about that?")
    await ctx.confirm("Delete this item?", on_yes=do_delete)
    await ctx.prompt("Sign Up", TextInput("name", "Name"), on_submit=handle)

All methods support {variable} placeholders:

    await ctx.success("Kicked **{member}**!", member=str(target))

And all accept the same keyword args as ctx.respond() (ephemeral, delete_after, etc.):

    await ctx.error("You don't have permission.", ephemeral=True)
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine

import discord

from .embed import Embed
from .components import Button, ActionRow, Modal, TextInput


# ---------------------------------------------------------------------------
# CuteContext
# ---------------------------------------------------------------------------

class CuteContext(discord.ApplicationContext):
    """
    Subclass of :class:`discord.ApplicationContext` with CuteCord shortcuts.

    Automatically used when you subclass :class:`~cutecord.Bot`.

    Quick reference
    ---------------
    ``ctx.embed(title, **vars)``      → Embed builder pre-configured (not sent yet)
    ``await ctx.success(msg, **vars)``  → ✅ green embed
    ``await ctx.error(msg, **vars)``    → ❌ red embed
    ``await ctx.info(msg, **vars)``     → ℹ️ blurple embed
    ``await ctx.warn(msg, **vars)``     → ⚠️ yellow embed
    ``await ctx.confirm(msg, ...)``     → embed + Yes/No buttons
    ``await ctx.prompt(title, *inputs, on_submit=...)`` → open a modal
    """

    # ------------------------------------------------------------------
    # Embed factory
    # ------------------------------------------------------------------

    def embed(self, title: str = "", **vars: Any) -> Embed:
        """
        Return a fresh :class:`~cutecord.Embed` builder pre-filled with *title*.

        Use this when you need more control than the one-liner helpers.

        Example
        -------
            embed = ctx.embed("Profile — {name}", name=ctx.author.display_name)
            embed.color("teal").field("ID", str(ctx.author.id))
            await ctx.respond(embed=embed.build())
        """
        return Embed(title, **vars)

    # ------------------------------------------------------------------
    # One-liner response helpers
    # ------------------------------------------------------------------

    async def success(
        self,
        message: str,
        *,
        title: str = "✅ Success",
        ephemeral: bool = False,
        delete_after: float | None = None,
        **vars: Any,
    ) -> discord.Interaction | discord.WebhookMessage:
        """
        Send a green success embed.

        Parameters
        ----------
        message:
            Body text.  Supports ``{variable}`` placeholders.
        title:
            Embed title (default: ``"✅ Success"``).
        ephemeral:
            Only visible to the invoking user.
        delete_after:
            Auto-delete after this many seconds.
        **vars:
            Values for ``{variable}`` placeholders in *message* and *title*.

        Example
        -------
            await ctx.success("Kicked **{member}**!", member=str(target))
        """
        embed = (
            Embed(title, **vars)
            .color("green")
            .description(message, **vars)
        )
        return await self.respond(
            embed=embed.build(),
            ephemeral=ephemeral,
            delete_after=delete_after,
        )

    async def error(
        self,
        message: str,
        *,
        title: str = "❌ Error",
        ephemeral: bool = True,
        delete_after: float | None = None,
        **vars: Any,
    ) -> discord.Interaction | discord.WebhookMessage:
        """
        Send a red error embed.  Ephemeral by default.

        Example
        -------
            await ctx.error("You don't have permission to do that.")
        """
        embed = (
            Embed(title, **vars)
            .color("red")
            .description(message, **vars)
        )
        return await self.respond(
            embed=embed.build(),
            ephemeral=ephemeral,
            delete_after=delete_after,
        )

    async def info(
        self,
        message: str,
        *,
        title: str = "ℹ️ Info",
        ephemeral: bool = False,
        delete_after: float | None = None,
        **vars: Any,
    ) -> discord.Interaction | discord.WebhookMessage:
        """
        Send a blurple info embed.

        Example
        -------
            await ctx.info("There are **{count}** members online.", count=42)
        """
        embed = (
            Embed(title, **vars)
            .color("blurple")
            .description(message, **vars)
        )
        return await self.respond(
            embed=embed.build(),
            ephemeral=ephemeral,
            delete_after=delete_after,
        )

    async def warn(
        self,
        message: str,
        *,
        title: str = "⚠️ Warning",
        ephemeral: bool = False,
        delete_after: float | None = None,
        **vars: Any,
    ) -> discord.Interaction | discord.WebhookMessage:
        """
        Send a yellow warning embed.

        Example
        -------
            await ctx.warn("This action cannot be undone.")
        """
        embed = (
            Embed(title, **vars)
            .color("yellow")
            .description(message, **vars)
        )
        return await self.respond(
            embed=embed.build(),
            ephemeral=ephemeral,
            delete_after=delete_after,
        )

    # ------------------------------------------------------------------
    # Confirmation dialog
    # ------------------------------------------------------------------

    async def confirm(
        self,
        message: str,
        *,
        title: str = "⚠️ Are you sure?",
        yes_label: str = "Yes",
        no_label: str = "Cancel",
        yes_style: str = "success",
        no_style: str = "secondary",
        ephemeral: bool = False,
        timeout: float = 60.0,
        on_yes: Callable[..., Coroutine[Any, Any, Any]] | None = None,
        on_no:  Callable[..., Coroutine[Any, Any, Any]] | None = None,
        **vars: Any,
    ) -> bool | None:
        """
        Send a confirmation embed with Yes / Cancel buttons.

        Returns ``True`` if the user clicked Yes, ``False`` if they clicked
        Cancel, or ``None`` if the timeout was reached.

        Parameters
        ----------
        message:
            Body text.  Supports ``{variable}`` placeholders.
        title:
            Embed title.
        yes_label / no_label:
            Button labels.
        yes_style / no_style:
            Button styles (``"success"``, ``"danger"``, ``"secondary"``…).
        ephemeral:
            Only the invoking user can see the message.
        timeout:
            Seconds to wait before giving up (default: 60).
        on_yes:
            Async callback ``(interaction) → None`` for the Yes button.
        on_no:
            Async callback ``(interaction) → None`` for the No button.
        **vars:
            Placeholder values for *message* and *title*.

        Example
        -------
            confirmed = await ctx.confirm(
                "Delete **{item}**?", item=item_name,
                yes_style="danger", yes_label="Delete it",
                on_yes=do_delete,
            )
            if confirmed:
                ...
        """
        embed = (
            Embed(title, **vars)
            .color("yellow")
            .description(message, **vars)
        )

        result: list[bool] = []
        event = asyncio.Event()

        async def _yes(interaction: discord.Interaction) -> None:
            result.append(True)
            event.set()
            if on_yes:
                await on_yes(interaction)
            elif not interaction.response.is_done():
                await interaction.response.defer()

        async def _no(interaction: discord.Interaction) -> None:
            result.append(False)
            event.set()
            if on_no:
                await on_no(interaction)
            elif not interaction.response.is_done():
                await interaction.response.defer()

        yes_btn = Button(yes_label, style=yes_style, custom_id="_cute_yes").on_click(_yes)
        no_btn  = Button(no_label,  style=no_style,  custom_id="_cute_no").on_click(_no)
        row = ActionRow().add(yes_btn).add(no_btn)

        await self.respond(embed=embed.build(), view=row.to_view(), ephemeral=ephemeral)

        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

        return result[0] if result else None

    # ------------------------------------------------------------------
    # Modal shortcut
    # ------------------------------------------------------------------

    async def prompt(
        self,
        title: str,
        *inputs: TextInput,
        on_submit: Callable[..., Coroutine[Any, Any, Any]] | None = None,
        custom_id: str = "",
    ) -> None:
        """
        Open a modal popup with one or more text inputs.

        Parameters
        ----------
        title:
            Modal window title (max 45 chars).
        *inputs:
            :class:`~cutecord.TextInput` fields to include.
        on_submit:
            Async callback ``(interaction, form) → None`` called on submission.
        custom_id:
            Optional custom ID for the modal.

        Example
        -------
            await ctx.prompt(
                "Change Nickname",
                TextInput("nick", "New nickname").max_length(32),
                on_submit=handle_nick,
            )

            async def handle_nick(interaction, form):
                nick = form.children[0].value
                await interaction.user.edit(nick=nick)
                await interaction.response.send_message(f"Nick set to **{nick}**!", ephemeral=True)
        """
        modal = Modal(title, custom_id=custom_id)
        for inp in inputs:
            modal.add(inp)
        if on_submit:
            modal.on_submit(on_submit)
        await self.send_modal(modal.build())

    # ------------------------------------------------------------------
    # Loading / thinking helper
    # ------------------------------------------------------------------

    async def thinking(self, ephemeral: bool = False) -> None:
        """
        Show a "Bot is thinking…" indicator while you process.
        Call ``ctx.respond()`` / ``ctx.edit()`` afterwards to replace it.

        Example
        -------
            await ctx.thinking()
            result = await some_slow_api_call()
            await ctx.edit(content=result)
        """
        await self.defer(ephemeral=ephemeral)
