"""
CuteCord Embed — a fluent, design-first Discord embed builder.

Supports:
  - Named color shortcuts  ("blurple", "red", "green", "gold", "dark", "white", …)
  - f-string-style variable interpolation in every text field
  - Loading images / thumbnails straight from file paths
  - Method chaining for compact, readable code

Example
-------
    embed = (
        Embed("Hello, {name}!", name="Alice")
        .color("blurple")
        .description("You joined **{server}**!", server="My Server")
        .thumbnail(from_file="avatar.png")
        .field("Score", "{score}/100", inline=True, score=42)
        .footer("Sent via CuteCord", icon="logo.png")
        .timestamp()
    )
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

import discord


# ---------------------------------------------------------------------------
# Named color palette
# ---------------------------------------------------------------------------

_COLORS: dict[str, int] = {
    "blurple":    0x5865F2,
    "fuchsia":    0xEB459E,
    "green":      0x57F287,
    "yellow":     0xFEE75C,
    "red":        0xED4245,
    "white":      0xFFFFFE,
    "dark":       0x2C2F33,
    "black":      0x23272A,
    "gold":       0xF1C40F,
    "orange":     0xE67E22,
    "teal":       0x1ABC9C,
    "purple":     0x9B59B6,
    "blue":       0x3498DB,
    "navy":       0x34495E,
    "pink":       0xFF69B4,
    "cyan":       0x00BCD4,
    "lime":       0x8BC34A,
    "indigo":     0x3F51B5,
    "transparent": discord.Color.default().value,
}


def _resolve_color(color: str | int | discord.Color | None) -> discord.Color:
    if color is None:
        return discord.Color.default()
    if isinstance(color, discord.Color):
        return color
    if isinstance(color, int):
        return discord.Color(color)
    lower = color.lower().strip()
    if lower in _COLORS:
        return discord.Color(_COLORS[lower])
    # Try hex string e.g. "#ff6600" or "ff6600"
    hex_str = lower.lstrip("#")
    try:
        return discord.Color(int(hex_str, 16))
    except ValueError:
        raise ValueError(
            f"Unknown color {color!r}. Use a name ({', '.join(_COLORS)}), "
            "an int, a discord.Color, or a hex string like '#ff6600'."
        )


def _fmt(text: str, **kwargs: Any) -> str:
    """Format *text* with *kwargs* using str.format_map (ignores missing keys)."""
    if not kwargs:
        return text

    class _SafeMap(dict):  # type: ignore[type-arg]
        def __missing__(self, key: str) -> str:
            return "{" + key + "}"

    return text.format_map(_SafeMap(**kwargs))


def _file_url(path: str | Path) -> str:
    """Return an ``attachment://`` URL for a local file path."""
    return f"attachment://{Path(path).name}"


# ---------------------------------------------------------------------------
# Embed
# ---------------------------------------------------------------------------

class Embed:
    """
    Fluent Discord embed builder.

    Parameters
    ----------
    title:
        Embed title.  Supports ``{variable}`` placeholders.
    **kwargs:
        Values used to fill ``{variable}`` placeholders in *title*.

    Example
    -------
        Embed("Welcome, {user}!", user="Alice").color("blurple")
    """

    def __init__(self, title: str = "", **kwargs: Any) -> None:
        self._title = _fmt(title, **kwargs)
        self._color: discord.Color = discord.Color.default()
        self._description: str = ""
        self._url: str = ""
        self._timestamp: datetime.datetime | None = None
        self._image_url: str = ""
        self._thumbnail_url: str = ""
        self._author_name: str = ""
        self._author_url: str = ""
        self._author_icon: str = ""
        self._footer_text: str = ""
        self._footer_icon: str = ""
        self._fields: list[dict[str, Any]] = []
        self._files: list[discord.File] = []

    # ------------------------------------------------------------------
    # Style
    # ------------------------------------------------------------------

    def color(self, color: str | int | discord.Color) -> "Embed":
        """Set the embed accent color.  Accepts a name, hex string, int, or discord.Color."""
        self._color = _resolve_color(color)
        return self

    colour = color  # British alias

    # ------------------------------------------------------------------
    # Core content
    # ------------------------------------------------------------------

    def description(self, text: str, **kwargs: Any) -> "Embed":
        """Set the embed body.  Supports ``{variable}`` placeholders."""
        self._description = _fmt(text, **kwargs)
        return self

    def url(self, href: str) -> "Embed":
        """Make the title a clickable link."""
        self._url = href
        return self

    def timestamp(self, dt: datetime.datetime | None = None) -> "Embed":
        """
        Add a timestamp footer.

        Parameters
        ----------
        dt:
            The datetime to display.  Defaults to ``datetime.datetime.now(tz=datetime.timezone.utc)``.
        """
        self._timestamp = dt or datetime.datetime.now(tz=datetime.timezone.utc)
        return self

    # ------------------------------------------------------------------
    # Media
    # ------------------------------------------------------------------

    def image(self, url: str = "", *, from_file: str | Path | None = None) -> "Embed":
        """
        Set the large image.

        Parameters
        ----------
        url:
            A public image URL.
        from_file:
            Path to a local image file.  CuteCord attaches it automatically.
        """
        if from_file is not None:
            path = Path(from_file)
            self._files.append(discord.File(path, filename=path.name))
            self._image_url = _file_url(path)
        else:
            self._image_url = url
        return self

    def thumbnail(self, url: str = "", *, from_file: str | Path | None = None) -> "Embed":
        """
        Set the small thumbnail (top-right corner).

        Parameters
        ----------
        url:
            A public image URL.
        from_file:
            Path to a local image file.  CuteCord attaches it automatically.
        """
        if from_file is not None:
            path = Path(from_file)
            self._files.append(discord.File(path, filename=path.name))
            self._thumbnail_url = _file_url(path)
        else:
            self._thumbnail_url = url
        return self

    # ------------------------------------------------------------------
    # Author
    # ------------------------------------------------------------------

    def author(
        self,
        name: str,
        url: str = "",
        icon: str | Path = "",
        **kwargs: Any,
    ) -> "Embed":
        """
        Set the embed author section.

        Parameters
        ----------
        name:
            Author display name.  Supports ``{variable}`` placeholders.
        url:
            Clickable URL on the author name.
        icon:
            URL or local file path for the author icon.
        **kwargs:
            Placeholder values for *name*.
        """
        self._author_name = _fmt(name, **kwargs)
        self._author_url = url
        icon_path = Path(icon) if icon else None
        if icon_path and icon_path.exists():
            self._files.append(discord.File(icon_path, filename=icon_path.name))
            self._author_icon = _file_url(icon_path)
        else:
            self._author_icon = str(icon)
        return self

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------

    def footer(
        self,
        text: str,
        icon: str | Path = "",
        **kwargs: Any,
    ) -> "Embed":
        """
        Set the embed footer.

        Parameters
        ----------
        text:
            Footer text.  Supports ``{variable}`` placeholders.
        icon:
            URL or local file path for the footer icon.
        **kwargs:
            Placeholder values for *text*.
        """
        self._footer_text = _fmt(text, **kwargs)
        icon_path = Path(icon) if icon else None
        if icon_path and icon_path.exists():
            self._files.append(discord.File(icon_path, filename=icon_path.name))
            self._footer_icon = _file_url(icon_path)
        else:
            self._footer_icon = str(icon)
        return self

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------

    def field(
        self,
        name: str,
        value: str = "\u200b",
        *,
        inline: bool = False,
        **kwargs: Any,
    ) -> "Embed":
        """
        Add an embed field.

        Parameters
        ----------
        name:
            Field title.  Supports ``{variable}`` placeholders.
        value:
            Field body.  Supports ``{variable}`` placeholders.
            Defaults to a zero-width space (keeps the field visible but empty).
        inline:
            Whether to place this field side-by-side with adjacent inline fields.
        **kwargs:
            Placeholder values for both *name* and *value*.
        """
        self._fields.append(
            {
                "name": _fmt(name, **kwargs),
                "value": _fmt(value, **kwargs),
                "inline": inline,
            }
        )
        return self

    def blank_field(self, *, inline: bool = False) -> "Embed":
        """Add an invisible spacer field."""
        return self.field("\u200b", "\u200b", inline=inline)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> discord.Embed:
        """Return the underlying :class:`discord.Embed` object."""
        embed = discord.Embed(
            title=self._title or None,
            description=self._description or None,
            color=self._color,
            url=self._url or None,
            timestamp=self._timestamp,
        )
        for f in self._fields:
            embed.add_field(name=f["name"], value=f["value"], inline=f["inline"])
        if self._image_url:
            embed.set_image(url=self._image_url)
        if self._thumbnail_url:
            embed.set_thumbnail(url=self._thumbnail_url)
        if self._author_name:
            embed.set_author(
                name=self._author_name,
                url=self._author_url or None,
                icon_url=self._author_icon or None,
            )
        if self._footer_text:
            embed.set_footer(
                text=self._footer_text,
                icon_url=self._footer_icon or None,
            )
        return embed

    @property
    def files(self) -> list[discord.File]:
        """Local files that must be sent alongside this embed."""
        return list(self._files)

    def to_dict(self) -> dict[str, Any]:
        """Return the embed as a raw JSON-serialisable dict."""
        return self.build().to_dict()

    # Allow passing a CuteEmbed directly to ctx.respond / channel.send
    def __discord_ui_kit_item__(self) -> discord.Embed:  # type: ignore[return-value]
        return self.build()
