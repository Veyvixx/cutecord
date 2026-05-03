"""
CuteCord Button — fluent Discord button builder.

Example
-------
    from cutecord.components import Button, ButtonStyle

    # Link button
    btn = Button("Visit Website", url="https://discord.com")

    # Interactive button with callback
    btn = (
        Button("Delete", style="danger", custom_id="delete_msg")
        .emoji("🗑️")
        .disabled(False)
    )

    # Shorthand style constructors
    btn = Button.primary("Confirm", custom_id="confirm")
    btn = Button.danger("Delete", custom_id="delete")
    btn = Button.success("Done", custom_id="done")
    btn = Button.secondary("Cancel", custom_id="cancel")
    btn = Button.link("Docs", url="https://discord.com/developers")
    btn = Button.premium(sku_id="1234567890")
"""

from __future__ import annotations

from typing import Any

import discord
from discord import ui


class ButtonStyle:
    Primary   = discord.ButtonStyle.primary
    Secondary = discord.ButtonStyle.secondary
    Success   = discord.ButtonStyle.success
    Danger    = discord.ButtonStyle.danger
    Link      = discord.ButtonStyle.link
    Premium   = discord.ButtonStyle.premium

    # Aliases
    Blurple = discord.ButtonStyle.primary
    Grey    = discord.ButtonStyle.secondary
    Gray    = discord.ButtonStyle.secondary
    Green   = discord.ButtonStyle.success
    Red     = discord.ButtonStyle.danger


_STYLE_MAP: dict[str, discord.ButtonStyle] = {
    "primary":   discord.ButtonStyle.primary,
    "secondary": discord.ButtonStyle.secondary,
    "success":   discord.ButtonStyle.success,
    "danger":    discord.ButtonStyle.danger,
    "link":      discord.ButtonStyle.link,
    "premium":   discord.ButtonStyle.premium,
    "blurple":   discord.ButtonStyle.primary,
    "grey":      discord.ButtonStyle.secondary,
    "gray":      discord.ButtonStyle.secondary,
    "green":     discord.ButtonStyle.success,
    "red":       discord.ButtonStyle.danger,
}


def _resolve_style(style: str | discord.ButtonStyle) -> discord.ButtonStyle:
    if isinstance(style, discord.ButtonStyle):
        return style
    key = style.lower().strip()
    if key not in _STYLE_MAP:
        raise ValueError(
            f"Unknown button style {style!r}. "
            f"Choose from: {', '.join(_STYLE_MAP)}"
        )
    return _STYLE_MAP[key]


class Button:
    """
    Fluent Discord button builder.

    Parameters
    ----------
    label:
        Button text (max 80 chars).
    style:
        Button style — a :class:`ButtonStyle` value or a string like
        ``"primary"``, ``"danger"``, ``"success"``, ``"secondary"``,
        ``"link"``, or ``"premium"``.
    custom_id:
        Developer-defined ID for interactive buttons (max 100 chars).
    url:
        URL for link-style buttons.  Pass this instead of *custom_id*.
    sku_id:
        SKU ID for premium-style buttons.
    row:
        Which ActionRow row to place this button on (0–4).

    Example
    -------
        btn = Button("Click me!", style="primary", custom_id="my_btn")
        btn.emoji("🎉").disabled(False)
    """

    def __init__(
        self,
        label: str = "",
        *,
        style: str | discord.ButtonStyle = "primary",
        custom_id: str | None = None,
        url: str | None = None,
        sku_id: str | None = None,
        row: int | None = None,
    ) -> None:
        self._label = label
        self._style = _resolve_style(style)
        self._custom_id = custom_id
        self._url = url
        self._sku_id = sku_id
        self._row = row
        self._emoji: str | discord.Emoji | discord.PartialEmoji | None = None
        self._disabled: bool = False
        self._callback: Any = None

    # ------------------------------------------------------------------
    # Fluent setters
    # ------------------------------------------------------------------

    def emoji(
        self,
        emoji: str | discord.Emoji | discord.PartialEmoji,
    ) -> "Button":
        """Add an emoji to the button (shown before the label)."""
        self._emoji = emoji
        return self

    def disabled(self, value: bool = True) -> "Button":
        """Disable or enable the button."""
        self._disabled = value
        return self

    def on_click(self, coro: Any) -> "Button":
        """Attach an async callback coroutine to this button's interaction."""
        self._callback = coro
        return self

    # ------------------------------------------------------------------
    # Style shortcuts
    # ------------------------------------------------------------------

    @classmethod
    def primary(cls, label: str, *, custom_id: str, **kwargs: Any) -> "Button":
        return cls(label, style="primary", custom_id=custom_id, **kwargs)

    @classmethod
    def secondary(cls, label: str, *, custom_id: str, **kwargs: Any) -> "Button":
        return cls(label, style="secondary", custom_id=custom_id, **kwargs)

    @classmethod
    def success(cls, label: str, *, custom_id: str, **kwargs: Any) -> "Button":
        return cls(label, style="success", custom_id=custom_id, **kwargs)

    @classmethod
    def danger(cls, label: str, *, custom_id: str, **kwargs: Any) -> "Button":
        return cls(label, style="danger", custom_id=custom_id, **kwargs)

    @classmethod
    def link(cls, label: str, *, url: str, **kwargs: Any) -> "Button":
        return cls(label, style="link", url=url, **kwargs)

    @classmethod
    def premium(cls, *, sku_id: str, **kwargs: Any) -> "Button":
        return cls("", style="premium", sku_id=sku_id, **kwargs)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> ui.Button:  # type: ignore[type-arg]
        """Return the underlying :class:`discord.ui.Button`."""
        btn: ui.Button = ui.Button(  # type: ignore[type-arg]
            label=self._label or None,
            style=self._style,
            custom_id=self._custom_id,
            url=self._url,
            emoji=self._emoji,
            disabled=self._disabled,
            row=self._row,
            sku_id=self._sku_id,
        )
        if self._callback is not None:
            btn.callback = self._callback
        return btn

    def to_component_dict(self) -> dict[str, Any]:
        """Return a raw component dict (for Components v2 payloads)."""
        d: dict[str, Any] = {
            "type": 2,
            "style": self._style.value,
            "disabled": self._disabled,
        }
        if self._label:
            d["label"] = self._label
        if self._custom_id:
            d["custom_id"] = self._custom_id
        if self._url:
            d["url"] = self._url
        if self._sku_id:
            d["sku_id"] = self._sku_id
        if self._emoji:
            if isinstance(self._emoji, str):
                d["emoji"] = {"name": self._emoji}
            elif isinstance(self._emoji, (discord.Emoji, discord.PartialEmoji)):
                d["emoji"] = {"id": str(self._emoji.id), "name": self._emoji.name}
        return d

    def __repr__(self) -> str:
        return f"Button(label={self._label!r}, style={self._style!r})"
