"""
CuteCord ActionRow — a container for up to 5 interactive components.

An ActionRow holds buttons or a single select menu.
You can have up to 5 ActionRows per message.

Example
-------
    from cutecord.components import ActionRow, Button, Select

    row = (
        ActionRow()
        .add(Button.primary("Yes", custom_id="yes"))
        .add(Button.danger("No",  custom_id="no"))
    )

    view = row.to_view()
    await ctx.respond("Are you sure?", view=view)
"""

from __future__ import annotations

from typing import Any, Union

import discord
from discord import ui

from .button import Button
from .select import Select, _AutoSelect


Addable = Union[Button, Select, "_AutoSelect"]


class ActionRow:
    """
    Fluent ActionRow builder.

    Parameters
    ----------
    row:
        Which row slot (0–4) this ActionRow occupies.

    Example
    -------
        row = ActionRow(row=0).add(Button.primary("Click", custom_id="c"))
        await ctx.respond("Hi!", view=row.to_view())
    """

    def __init__(self, *, row: int = 0) -> None:
        self._row = row
        self._items: list[Addable] = []

    def add(self, component: Addable) -> "ActionRow":
        """
        Add a component to this row.

        Accepts :class:`~cutecord.components.Button`,
        :class:`~cutecord.components.Select`, or any auto-select type.
        """
        if len(self._items) >= 5:
            raise ValueError("An ActionRow can hold at most 5 components.")
        self._items.append(component)
        return self

    def build_items(self) -> list[Any]:
        """Return a list of built discord.py component objects."""
        return [item.build() for item in self._items]

    def to_view(self) -> ui.View:
        """
        Return a :class:`discord.ui.View` containing just this ActionRow.

        Pass directly to ``ctx.respond(view=...)`` or ``channel.send(view=...)``.
        """
        view = ui.View()
        for item in self.build_items():
            view.add_item(item)
        return view

    def to_component_dict(self) -> dict[str, Any]:
        """Return a raw Components v2 dict for this row."""
        return {
            "type": 1,
            "components": [item.to_component_dict() for item in self._items],
        }

    def __repr__(self) -> str:
        return f"ActionRow(row={self._row}, items={len(self._items)})"


def build_view(*rows: ActionRow) -> ui.View:
    """
    Build a :class:`discord.ui.View` from one or more :class:`ActionRow` objects.

    Parameters
    ----------
    *rows:
        Up to 5 ActionRow instances.

    Example
    -------
        view = build_view(
            ActionRow().add(Button.primary("Confirm", custom_id="ok")),
            ActionRow().add(Button.secondary("Cancel", custom_id="cancel")),
        )
        await ctx.respond("Ready?", view=view)
    """
    if len(rows) > 5:
        raise ValueError("A message can have at most 5 ActionRows.")
    view = ui.View()
    for row in rows:
        for item in row.build_items():
            view.add_item(item)
    return view
