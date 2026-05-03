"""
CuteCord Select Menus — fluent builders for all five Discord select menu types.

Types
-----
    Select            — string dropdown (you define the options)
    UserSelect        — picks Discord users
    RoleSelect        — picks roles
    MentionableSelect — picks users OR roles
    ChannelSelect     — picks channels

Example
-------
    from cutecord.components import Select

    menu = (
        Select("pick_colour", placeholder="Pick a colour…")
        .option("Red",   "red",   emoji="🔴", description="Fiery red")
        .option("Green", "green", emoji="🟢")
        .option("Blue",  "blue",  emoji="🔵", default=True)
        .min(1).max(1)
    )

    user_menu = UserSelect("pick_user", placeholder="Mention someone…").max(3)
"""

from __future__ import annotations

from typing import Any

import discord
from discord import ui


# ---------------------------------------------------------------------------
# String Select (custom options)
# ---------------------------------------------------------------------------

class Select:
    """
    Fluent string select menu builder.

    Parameters
    ----------
    custom_id:
        Developer-defined ID (max 100 chars).
    placeholder:
        Grey hint text shown when nothing is selected.
    row:
        Which ActionRow row to place this component on (0–4).
    """

    def __init__(
        self,
        custom_id: str,
        placeholder: str = "",
        *,
        row: int | None = None,
    ) -> None:
        self._custom_id = custom_id
        self._placeholder = placeholder
        self._row = row
        self._min_values: int = 1
        self._max_values: int = 1
        self._disabled: bool = False
        self._options: list[discord.SelectOption] = []
        self._callback: Any = None

    # ------------------------------------------------------------------
    # Options
    # ------------------------------------------------------------------

    def option(
        self,
        label: str,
        value: str,
        *,
        description: str = "",
        emoji: str | discord.Emoji | discord.PartialEmoji | None = None,
        default: bool = False,
    ) -> "Select":
        """
        Add a selectable option.

        Parameters
        ----------
        label:
            Display text (max 100 chars).
        value:
            Developer value returned when selected (max 100 chars).
        description:
            Small grey description shown under the label.
        emoji:
            Emoji shown to the left of the label.
        default:
            Pre-select this option.
        """
        self._options.append(
            discord.SelectOption(
                label=label,
                value=value,
                description=description or None,
                emoji=emoji,
                default=default,
            )
        )
        return self

    def options(self, *opts: discord.SelectOption) -> "Select":
        """Bulk-add :class:`discord.SelectOption` objects."""
        self._options.extend(opts)
        return self

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------

    def min(self, n: int) -> "Select":
        """Minimum number of selections (1–25)."""
        self._min_values = n
        return self

    def max(self, n: int) -> "Select":
        """Maximum number of selections (1–25)."""
        self._max_values = n
        return self

    def disabled(self, value: bool = True) -> "Select":
        self._disabled = value
        return self

    def on_select(self, coro: Any) -> "Select":
        """Attach an async callback coroutine."""
        self._callback = coro
        return self

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> ui.Select:  # type: ignore[type-arg]
        sel: ui.Select = ui.Select(  # type: ignore[type-arg]
            custom_id=self._custom_id,
            placeholder=self._placeholder or None,
            min_values=self._min_values,
            max_values=self._max_values,
            options=self._options,
            disabled=self._disabled,
            row=self._row,
        )
        if self._callback is not None:
            sel.callback = self._callback
        return sel

    def to_component_dict(self) -> dict[str, Any]:
        return {
            "type": 3,
            "custom_id": self._custom_id,
            "placeholder": self._placeholder or None,
            "min_values": self._min_values,
            "max_values": self._max_values,
            "disabled": self._disabled,
            "options": [
                {
                    "label": o.label,
                    "value": o.value,
                    "description": o.description,
                    "default": o.default,
                }
                for o in self._options
            ],
        }

    def __repr__(self) -> str:
        return f"Select(custom_id={self._custom_id!r}, options={len(self._options)})"


# ---------------------------------------------------------------------------
# Generic auto-populated select base
# ---------------------------------------------------------------------------

class _AutoSelect:
    _discord_type: type[ui.BaseSelect]  # type: ignore[type-arg]
    _component_type: int

    def __init__(
        self,
        custom_id: str,
        placeholder: str = "",
        *,
        row: int | None = None,
    ) -> None:
        self._custom_id = custom_id
        self._placeholder = placeholder
        self._row = row
        self._min_values: int = 1
        self._max_values: int = 1
        self._disabled: bool = False
        self._default_values: list[Any] = []
        self._callback: Any = None

    def min(self, n: int) -> "_AutoSelect":
        self._min_values = n
        return self

    def max(self, n: int) -> "_AutoSelect":
        self._max_values = n
        return self

    def disabled(self, value: bool = True) -> "_AutoSelect":
        self._disabled = value
        return self

    def on_select(self, coro: Any) -> "_AutoSelect":
        self._callback = coro
        return self

    def build(self) -> ui.BaseSelect:  # type: ignore[type-arg]
        sel = self._discord_type(  # type: ignore[call-arg]
            custom_id=self._custom_id,
            placeholder=self._placeholder or None,
            min_values=self._min_values,
            max_values=self._max_values,
            disabled=self._disabled,
            row=self._row,
        )
        if self._callback is not None:
            sel.callback = self._callback
        return sel

    def to_component_dict(self) -> dict[str, Any]:
        return {
            "type": self._component_type,
            "custom_id": self._custom_id,
            "placeholder": self._placeholder or None,
            "min_values": self._min_values,
            "max_values": self._max_values,
            "disabled": self._disabled,
        }

    def __repr__(self) -> str:
        return f"{type(self).__name__}(custom_id={self._custom_id!r})"


# ---------------------------------------------------------------------------
# Concrete auto-populated selects
# ---------------------------------------------------------------------------

class UserSelect(_AutoSelect):
    """
    Select menu that lists Discord users.

    Example
    -------
        menu = UserSelect("pick_user", "Choose a user…").max(3)
    """
    _discord_type = ui.UserSelect  # type: ignore[assignment]
    _component_type = 5


class RoleSelect(_AutoSelect):
    """
    Select menu that lists server roles.

    Example
    -------
        menu = RoleSelect("pick_role", "Choose a role…")
    """
    _discord_type = ui.RoleSelect  # type: ignore[assignment]
    _component_type = 6


class MentionableSelect(_AutoSelect):
    """
    Select menu that lists both users and roles.

    Example
    -------
        menu = MentionableSelect("pick_any", "Mention someone or a role…")
    """
    _discord_type = ui.MentionableSelect  # type: ignore[assignment]
    _component_type = 7


class ChannelSelect(_AutoSelect):
    """
    Select menu that lists server channels.

    Example
    -------
        menu = ChannelSelect("pick_channel", "Pick a channel…")
    """
    _discord_type = ui.ChannelSelect  # type: ignore[assignment]
    _component_type = 8
