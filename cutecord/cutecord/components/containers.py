"""
CuteCord Containers — Discord Components v2 layout blocks.

These map to the newer Discord "Components v2" system (requires the
``IS_COMPONENTS_V2`` message flag).  Use them by building a raw payload
dict and sending it via the Discord API directly, or via a library that
supports Components v2.

Components
----------
    Container       — coloured wrapper grouping multiple sub-components
    Section         — side-by-side layout: text block + optional accessory
    TextDisplay     — rich markdown text block
    Thumbnail       — image accessory (used as Section accessory)
    MediaGallery    — 1–10 image/video grid
    MediaGalleryItem — single item inside a MediaGallery
    FileComponent   — uploaded file display block
    Separator       — horizontal divider with optional spacing
    Header          — heading text (H1 / H2 / H3)

Example
-------
    from cutecord.components import (
        Container, Section, TextDisplay, Thumbnail,
        MediaGallery, MediaGalleryItem, Separator, Header, HeadingLevel,
    )

    layout = (
        Container(color="blurple")
        .add(Header("Welcome!", level=HeadingLevel.One))
        .add(Separator())
        .add(
            Section()
            .content(TextDisplay("Here is your profile."))
            .accessory(Thumbnail("https://example.com/avatar.png"))
        )
        .add(Separator(spacing="large", divider=False))
        .add(
            MediaGallery()
            .item(MediaGalleryItem("https://example.com/img1.png", description="Photo 1"))
            .item(MediaGalleryItem("https://example.com/img2.png"))
        )
    )

    payload = layout.to_component_dict()
"""

from __future__ import annotations

from enum import IntEnum
from pathlib import Path
from typing import Any, Union


# ---------------------------------------------------------------------------
# Color helper (reuse embed palette)
# ---------------------------------------------------------------------------

_COLORS: dict[str, int] = {
    "blurple":  0x5865F2,
    "fuchsia":  0xEB459E,
    "green":    0x57F287,
    "yellow":   0xFEE75C,
    "red":      0xED4245,
    "white":    0xFFFFFE,
    "dark":     0x2C2F33,
    "gold":     0xF1C40F,
    "orange":   0xE67E22,
    "teal":     0x1ABC9C,
    "purple":   0x9B59B6,
    "blue":     0x3498DB,
}


def _color_int(color: str | int | None) -> int | None:
    if color is None:
        return None
    if isinstance(color, int):
        return color
    lower = color.lower().strip()
    if lower in _COLORS:
        return _COLORS[lower]
    try:
        return int(lower.lstrip("#"), 16)
    except ValueError:
        raise ValueError(f"Unknown color {color!r}.")


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SeparatorSpacing(IntEnum):
    Small = 1
    Large = 2


class HeadingLevel(IntEnum):
    One   = 1
    Two   = 2
    Three = 3

    H1 = 1
    H2 = 2
    H3 = 3


# ---------------------------------------------------------------------------
# TextDisplay (type 10)
# ---------------------------------------------------------------------------

class TextDisplay:
    """
    A markdown text block for use inside Containers and Sections.

    Parameters
    ----------
    content:
        The markdown text to display.
    id:
        Optional component ID.

    Example
    -------
        TextDisplay("**Hello!** Welcome to the server.")
    """

    def __init__(self, content: str, *, id: int | None = None) -> None:
        self._content = content
        self._id = id

    def to_component_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"type": 10, "content": self._content}
        if self._id is not None:
            d["id"] = self._id
        return d

    def __repr__(self) -> str:
        return f"TextDisplay({self._content[:40]!r})"


# ---------------------------------------------------------------------------
# Thumbnail (type 11) — used as a Section accessory
# ---------------------------------------------------------------------------

class Thumbnail:
    """
    A small image accessory, typically placed inside a :class:`Section`.

    Parameters
    ----------
    url:
        Image URL or ``attachment://filename.png`` for uploads.
    from_file:
        Local file path; generates the ``attachment://`` URL automatically.
    description:
        Alt-text / accessibility description.
    spoiler:
        Blur the image until clicked.
    id:
        Optional component ID.

    Example
    -------
        Thumbnail("https://example.com/avatar.png", description="User avatar")
        Thumbnail(from_file="logo.png")
    """

    def __init__(
        self,
        url: str = "",
        *,
        from_file: str | Path | None = None,
        description: str = "",
        spoiler: bool = False,
        id: int | None = None,
    ) -> None:
        if from_file is not None:
            p = Path(from_file)
            self._url = f"attachment://{p.name}"
        else:
            self._url = url
        self._description = description
        self._spoiler = spoiler
        self._id = id

    def to_component_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": 11,
            "media": {"url": self._url},
        }
        if self._description:
            d["description"] = self._description
        if self._spoiler:
            d["spoiler"] = True
        if self._id is not None:
            d["id"] = self._id
        return d

    def __repr__(self) -> str:
        return f"Thumbnail(url={self._url!r})"


# ---------------------------------------------------------------------------
# MediaGalleryItem
# ---------------------------------------------------------------------------

class MediaGalleryItem:
    """
    A single media item inside a :class:`MediaGallery`.

    Parameters
    ----------
    url:
        Image or video URL.
    from_file:
        Local file path; generates the ``attachment://`` URL automatically.
    description:
        Alt-text for the item.
    spoiler:
        Blur the item.

    Example
    -------
        MediaGalleryItem("https://cdn.example.com/img.png", description="Cool photo")
    """

    def __init__(
        self,
        url: str = "",
        *,
        from_file: str | Path | None = None,
        description: str = "",
        spoiler: bool = False,
    ) -> None:
        if from_file is not None:
            p = Path(from_file)
            self._url = f"attachment://{p.name}"
        else:
            self._url = url
        self._description = description
        self._spoiler = spoiler

    def to_component_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"media": {"url": self._url}}
        if self._description:
            d["description"] = self._description
        if self._spoiler:
            d["spoiler"] = True
        return d


# ---------------------------------------------------------------------------
# MediaGallery (type 12)
# ---------------------------------------------------------------------------

class MediaGallery:
    """
    A 1–10 item grid of images or videos.

    Example
    -------
        gallery = (
            MediaGallery()
            .item(MediaGalleryItem("https://example.com/a.png"))
            .item(MediaGalleryItem("https://example.com/b.png", description="Second"))
        )
    """

    def __init__(self, *, id: int | None = None) -> None:
        self._items: list[MediaGalleryItem] = []
        self._id = id

    def item(self, media_item: MediaGalleryItem) -> "MediaGallery":
        """Add a :class:`MediaGalleryItem` to the gallery."""
        if len(self._items) >= 10:
            raise ValueError("MediaGallery supports at most 10 items.")
        self._items.append(media_item)
        return self

    def to_component_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": 12,
            "items": [i.to_component_dict() for i in self._items],
        }
        if self._id is not None:
            d["id"] = self._id
        return d

    def __repr__(self) -> str:
        return f"MediaGallery(items={len(self._items)})"


# ---------------------------------------------------------------------------
# FileComponent (type 13)
# ---------------------------------------------------------------------------

class FileComponent:
    """
    Display an uploaded file attachment inline.

    Parameters
    ----------
    url:
        ``attachment://filename`` reference to an uploaded file.
    from_file:
        Local file path; generates the ``attachment://`` URL automatically.
    spoiler:
        Blur the file preview.
    id:
        Optional component ID.

    Example
    -------
        FileComponent(from_file="report.pdf")
    """

    def __init__(
        self,
        url: str = "",
        *,
        from_file: str | Path | None = None,
        spoiler: bool = False,
        id: int | None = None,
    ) -> None:
        if from_file is not None:
            p = Path(from_file)
            self._url = f"attachment://{p.name}"
        else:
            self._url = url
        self._spoiler = spoiler
        self._id = id

    def to_component_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": 13,
            "file": {"url": self._url},
        }
        if self._spoiler:
            d["spoiler"] = True
        if self._id is not None:
            d["id"] = self._id
        return d


# ---------------------------------------------------------------------------
# Separator (type 14)
# ---------------------------------------------------------------------------

class Separator:
    """
    A horizontal divider line with optional spacing.

    Parameters
    ----------
    spacing:
        ``"small"`` (default) or ``"large"``.  Also accepts
        :class:`SeparatorSpacing` enum values.
    divider:
        Show the visible line.  Set to ``False`` for invisible spacing only.
    id:
        Optional component ID.

    Example
    -------
        Separator()                        # thin line, small gap
        Separator(spacing="large")         # thin line, large gap
        Separator(spacing="large", divider=False)  # invisible spacer
    """

    _SPACING_MAP = {"small": SeparatorSpacing.Small, "large": SeparatorSpacing.Large}

    def __init__(
        self,
        spacing: str | SeparatorSpacing = "small",
        *,
        divider: bool = True,
        id: int | None = None,
    ) -> None:
        if isinstance(spacing, str):
            key = spacing.lower().strip()
            if key not in self._SPACING_MAP:
                raise ValueError(f"spacing must be 'small' or 'large', got {spacing!r}")
            self._spacing = self._SPACING_MAP[key]
        else:
            self._spacing = spacing
        self._divider = divider
        self._id = id

    def to_component_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": 14,
            "spacing": self._spacing.value,
            "divider": self._divider,
        }
        if self._id is not None:
            d["id"] = self._id
        return d

    def __repr__(self) -> str:
        return f"Separator(spacing={self._spacing.name!r}, divider={self._divider})"


# ---------------------------------------------------------------------------
# Header (type 17)
# ---------------------------------------------------------------------------

class Header:
    """
    A heading text block (H1, H2, or H3).

    Parameters
    ----------
    content:
        The heading text.
    level:
        Heading level — 1, 2, or 3 (or a :class:`HeadingLevel` value).
    id:
        Optional component ID.

    Example
    -------
        Header("Server Rules", level=HeadingLevel.One)
        Header("Channel Info", level=2)
    """

    def __init__(
        self,
        content: str,
        *,
        level: int | HeadingLevel = HeadingLevel.One,
        id: int | None = None,
    ) -> None:
        if isinstance(level, int):
            if level not in (1, 2, 3):
                raise ValueError(f"Heading level must be 1, 2, or 3; got {level}")
            self._level = HeadingLevel(level)
        else:
            self._level = level
        self._content = content
        self._id = id

    def to_component_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": 17,
            "content": self._content,
            "level": self._level.value,
        }
        if self._id is not None:
            d["id"] = self._id
        return d

    def __repr__(self) -> str:
        return f"Header({self._content!r}, level={self._level.value})"


# ---------------------------------------------------------------------------
# Section (type 9)
# ---------------------------------------------------------------------------

_SectionContent = Union[TextDisplay, "Section"]
_SectionAccessory = Union[Thumbnail, "Button"]  # type: ignore[name-defined]


class Section:
    """
    A side-by-side layout component: text content on the left, optional
    accessory (thumbnail or button) on the right.

    Example
    -------
        section = (
            Section()
            .content(TextDisplay("Your profile is all set!"))
            .accessory(Thumbnail("https://example.com/avatar.png"))
        )
    """

    def __init__(self, *, id: int | None = None) -> None:
        self._components: list[Any] = []
        self._accessory: Any = None
        self._id = id

    def content(self, *components: Any) -> "Section":
        """Add text display components to the left side."""
        self._components.extend(components)
        return self

    def accessory(self, component: Any) -> "Section":
        """Set the right-side accessory (Thumbnail or Button)."""
        self._accessory = component
        return self

    def to_component_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": 9,
            "components": [c.to_component_dict() for c in self._components],
        }
        if self._accessory is not None:
            d["accessory"] = self._accessory.to_component_dict()
        if self._id is not None:
            d["id"] = self._id
        return d

    def __repr__(self) -> str:
        return f"Section(components={len(self._components)})"


# ---------------------------------------------------------------------------
# Container (type 17)
# ---------------------------------------------------------------------------

class Container:
    """
    A coloured wrapper grouping multiple sub-components.

    The Container requires the ``IS_COMPONENTS_V2`` message flag.

    Parameters
    ----------
    color:
        Accent color — a name (``"blurple"``, ``"red"``…), hex string, or int.
    spoiler:
        Collapse the container behind a spoiler.
    id:
        Optional component ID.

    Example
    -------
        card = (
            Container(color="blurple")
            .add(Header("Welcome!"))
            .add(Separator())
            .add(TextDisplay("Here is some info."))
        )
    """

    def __init__(
        self,
        color: str | int | None = None,
        *,
        spoiler: bool = False,
        id: int | None = None,
    ) -> None:
        self._color = _color_int(color)
        self._spoiler = spoiler
        self._id = id
        self._components: list[Any] = []

    def add(self, component: Any) -> "Container":
        """Append a component to the container."""
        self._components.append(component)
        return self

    def to_component_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "type": 17,
            "components": [c.to_component_dict() for c in self._components],
        }
        if self._color is not None:
            d["accent_color"] = self._color
        if self._spoiler:
            d["spoiler"] = True
        if self._id is not None:
            d["id"] = self._id
        return d

    def to_message_payload(self) -> dict[str, Any]:
        """
        Return a full message payload dict (including the Components v2 flag).

        Pass ``**container.to_message_payload()`` to your HTTP client's
        ``send_message`` / ``create_message`` call.
        """
        return {
            "components": [self.to_component_dict()],
            "flags": 1 << 15,  # IS_COMPONENTS_V2
        }

    def __repr__(self) -> str:
        return f"Container(color={self._color!r}, components={len(self._components)})"
