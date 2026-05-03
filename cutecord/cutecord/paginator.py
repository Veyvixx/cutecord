"""
CuteCord Paginator — split long content across multiple embed pages
with automatic Previous / Next buttons.

Usage
-----
    from cutecord.paginator import Paginator

    pages = [
        Embed("Page 1").color("blurple").description("First page content"),
        Embed("Page 2").color("blurple").description("Second page content"),
        Embed("Page 3").color("blurple").description("Third page content"),
    ]

    pager = Paginator(pages, loop=True, show_index=True)
    await pager.send(ctx)

Or build pages from a list of strings automatically:

    pager = Paginator.from_lines(
        lines=long_list_of_strings,
        title="Results",
        color="teal",
        per_page=10,
    )
    await pager.send(ctx)
"""

from __future__ import annotations

import discord
from discord import ui

from .embed import Embed


class Paginator:
    """
    A paginated embed with Previous / Next navigation buttons.

    Parameters
    ----------
    pages:
        List of :class:`~cutecord.Embed` objects (one per page).
    loop:
        Whether to wrap around from the last page back to the first.
    show_index:
        Append "Page X / Y" to each embed's footer.
    timeout:
        Seconds before the buttons are disabled (default: 120).

    Example
    -------
        pager = Paginator([
            Embed("Page 1").description("Hello"),
            Embed("Page 2").description("World"),
        ])
        await pager.send(ctx)
    """

    def __init__(
        self,
        pages: list[Embed],
        *,
        loop: bool = False,
        show_index: bool = True,
        timeout: float = 120.0,
    ) -> None:
        if not pages:
            raise ValueError("Paginator requires at least one page.")
        self._pages = pages
        self._loop = loop
        self._show_index = show_index
        self._timeout = timeout
        self._index = 0

    # ------------------------------------------------------------------
    # Factory: build pages from a list of lines
    # ------------------------------------------------------------------

    @classmethod
    def from_lines(
        cls,
        lines: list[str],
        *,
        title: str = "",
        color: str = "blurple",
        per_page: int = 10,
        loop: bool = False,
        show_index: bool = True,
        timeout: float = 120.0,
        join: str = "\n",
    ) -> "Paginator":
        """
        Build a paginator from a flat list of strings.

        Parameters
        ----------
        lines:
            All the lines to paginate.
        title:
            Title for every page embed.
        color:
            Embed color (name or hex).
        per_page:
            Lines per page (default: 10).
        join:
            String used to join lines within a page (default: newline).

        Example
        -------
            members = [str(m) for m in ctx.guild.members]
            pager = Paginator.from_lines(members, title="Members", per_page=15)
            await pager.send(ctx)
        """
        pages = []
        for i in range(0, max(len(lines), 1), per_page):
            chunk = lines[i : i + per_page]
            embed = Embed(title).color(color).description(join.join(chunk))
            pages.append(embed)
        return cls(pages, loop=loop, show_index=show_index, timeout=timeout)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _current_embed(self) -> discord.Embed:
        embed = self._pages[self._index]
        if self._show_index:
            existing_footer = embed._footer_text
            footer = f"Page {self._index + 1}/{len(self._pages)}"
            if existing_footer:
                footer = f"{existing_footer}  •  {footer}"
            # Clone the embed to avoid mutating the original
            clone = Embed(embed._title)
            clone._color = embed._color
            clone._description = embed._description
            clone._url = embed._url
            clone._timestamp = embed._timestamp
            clone._image_url = embed._image_url
            clone._thumbnail_url = embed._thumbnail_url
            clone._author_name = embed._author_name
            clone._author_url = embed._author_url
            clone._author_icon = embed._author_icon
            clone._footer_text = footer
            clone._footer_icon = embed._footer_icon
            clone._fields = list(embed._fields)
            return clone.build()
        return embed.build()

    def _make_view(self, author_id: int) -> ui.View:
        pager = self
        total = len(self._pages)

        class PaginatorView(ui.View):
            def __init__(self_v) -> None:
                super().__init__(timeout=pager._timeout)
                self_v.author_id = author_id

            async def interaction_check(self_v, interaction: discord.Interaction) -> bool:
                if interaction.user.id != self_v.author_id:
                    await interaction.response.send_message(
                        "Only the command invoker can flip pages.", ephemeral=True
                    )
                    return False
                return True

            async def on_timeout(self_v) -> None:
                for child in self_v.children:
                    child.disabled = True  # type: ignore[attr-defined]

            @ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
            async def first(self_v, btn: ui.Button, interaction: discord.Interaction):
                pager._index = 0
                await interaction.response.edit_message(embed=pager._current_embed(), view=self_v)

            @ui.button(emoji="◀️", style=discord.ButtonStyle.primary)
            async def prev(self_v, btn: ui.Button, interaction: discord.Interaction):
                if pager._index > 0:
                    pager._index -= 1
                elif pager._loop:
                    pager._index = total - 1
                await interaction.response.edit_message(embed=pager._current_embed(), view=self_v)

            @ui.button(emoji="▶️", style=discord.ButtonStyle.primary)
            async def next(self_v, btn: ui.Button, interaction: discord.Interaction):
                if pager._index < total - 1:
                    pager._index += 1
                elif pager._loop:
                    pager._index = 0
                await interaction.response.edit_message(embed=pager._current_embed(), view=self_v)

            @ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
            async def last(self_v, btn: ui.Button, interaction: discord.Interaction):
                pager._index = total - 1
                await interaction.response.edit_message(embed=pager._current_embed(), view=self_v)

        return PaginatorView()

    # ------------------------------------------------------------------
    # Send
    # ------------------------------------------------------------------

    async def send(
        self,
        ctx: discord.ApplicationContext,
        *,
        ephemeral: bool = False,
    ) -> None:
        """
        Send the paginator to the given context.

        Parameters
        ----------
        ctx:
            The slash command context.
        ephemeral:
            Only visible to the invoking user.

        Example
        -------
            pager = Paginator(pages)
            await pager.send(ctx)
        """
        view = self._make_view(ctx.author.id)
        if len(self._pages) == 1:
            await ctx.respond(embed=self._current_embed(), ephemeral=ephemeral)
        else:
            await ctx.respond(embed=self._current_embed(), view=view, ephemeral=ephemeral)
