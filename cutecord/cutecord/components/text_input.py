"""
CuteCord TextInput — fluent builder for Discord modal text fields.

Example
-------
    from cutecord.components import TextInput, TextInputStyle

    name_field = (
        TextInput("your_name", "Your name")
        .placeholder("e.g. Alice")
        .required(True)
        .min_length(2)
        .max_length(50)
    )

    bio_field = (
        TextInput("bio", "Tell us about yourself", style="paragraph")
        .placeholder("I like Discord bots…")
        .max_length(300)
        .required(False)
    )
"""

from __future__ import annotations

import discord
from discord import ui


class TextInputStyle:
    Short     = discord.TextStyle.short
    Paragraph = discord.TextStyle.paragraph
    Long      = discord.TextStyle.paragraph  # alias


_STYLE_MAP: dict[str, discord.TextStyle] = {
    "short":     discord.TextStyle.short,
    "paragraph": discord.TextStyle.paragraph,
    "long":      discord.TextStyle.paragraph,
}


def _resolve_style(style: str | discord.TextStyle) -> discord.TextStyle:
    if isinstance(style, discord.TextStyle):
        return style
    key = style.lower().strip()
    if key not in _STYLE_MAP:
        raise ValueError(
            f"Unknown TextInput style {style!r}. Choose from: {', '.join(_STYLE_MAP)}"
        )
    return _STYLE_MAP[key]


class TextInput:
    """
    Fluent Discord text input builder (for use inside a :class:`~cutecord.components.Modal`).

    Parameters
    ----------
    custom_id:
        Developer-defined ID (max 100 chars).
    label:
        Label shown above the input field (max 45 chars).
    style:
        ``"short"`` (single line) or ``"paragraph"`` (multi-line).
    """

    def __init__(
        self,
        custom_id: str,
        label: str,
        *,
        style: str | discord.TextStyle = "short",
    ) -> None:
        self._custom_id = custom_id
        self._label = label
        self._style = _resolve_style(style)
        self._placeholder: str = ""
        self._value: str = ""
        self._required: bool = True
        self._min_length: int | None = None
        self._max_length: int | None = None
        self._row: int | None = None

    # ------------------------------------------------------------------
    # Fluent setters
    # ------------------------------------------------------------------

    def placeholder(self, text: str) -> "TextInput":
        """Grey hint text displayed inside the empty input."""
        self._placeholder = text
        return self

    def default(self, text: str) -> "TextInput":
        """Pre-filled value shown inside the input."""
        self._value = text
        return self

    def required(self, value: bool = True) -> "TextInput":
        """Whether the user must fill this field before submitting."""
        self._required = value
        return self

    def min_length(self, n: int) -> "TextInput":
        """Minimum number of characters required."""
        self._min_length = n
        return self

    def max_length(self, n: int) -> "TextInput":
        """Maximum number of characters allowed (max 4000)."""
        self._max_length = n
        return self

    def row(self, n: int) -> "TextInput":
        """Row position inside the modal (0–4)."""
        self._row = n
        return self

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> ui.TextInput:  # type: ignore[type-arg]
        """Return the underlying :class:`discord.ui.TextInput`."""
        return ui.TextInput(
            custom_id=self._custom_id,
            label=self._label,
            style=self._style,
            placeholder=self._placeholder or None,
            default=self._value or None,
            required=self._required,
            min_length=self._min_length,
            max_length=self._max_length,
            row=self._row,
        )

    def to_component_dict(self) -> dict:
        d: dict = {
            "type": 4,
            "custom_id": self._custom_id,
            "label": self._label,
            "style": self._style.value,
            "required": self._required,
        }
        if self._placeholder:
            d["placeholder"] = self._placeholder
        if self._value:
            d["value"] = self._value
        if self._min_length is not None:
            d["min_length"] = self._min_length
        if self._max_length is not None:
            d["max_length"] = self._max_length
        return d

    def __repr__(self) -> str:
        return f"TextInput(custom_id={self._custom_id!r}, label={self._label!r})"
