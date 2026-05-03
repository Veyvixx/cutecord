"""
CuteCord Modal — fluent Discord modal (popup form) builder.

Example
-------
    from cutecord.components import Modal, TextInput

    class FeedbackModal(Modal.as_class("Share Feedback", custom_id="feedback")):
        subject = TextInput("subject", "Subject").max_length(100).build()
        body    = TextInput("body", "Message", style="paragraph").max_length(1000).build()

        async def callback(self, interaction):
            await interaction.response.send_message(
                f"Got it! **{self.subject.value}**", ephemeral=True
            )

    # --- OR use the builder API ---

    async def ask_name(ctx):
        modal = (
            Modal("What's your name?", custom_id="ask_name")
            .add(TextInput("name", "Your name").placeholder("Alice").max_length(50))
            .on_submit(handle_name)
        )
        await ctx.send_modal(modal.build())
"""

from __future__ import annotations

from typing import Any, Callable, Coroutine

import discord
from discord import ui

from .text_input import TextInput


class Modal:
    """
    Fluent Discord modal builder.

    Parameters
    ----------
    title:
        Modal window title (max 45 chars).
    custom_id:
        Developer-defined ID (max 100 chars).  Auto-generated if omitted.

    Example
    -------
        modal = (
            Modal("Sign up", custom_id="signup")
            .add(TextInput("name", "Your name").max_length(50))
            .add(TextInput("email", "Email", style="short"))
            .on_submit(my_handler)
        )
        await ctx.send_modal(modal.build())
    """

    def __init__(self, title: str, *, custom_id: str = "") -> None:
        self._title = title
        self._custom_id = custom_id or f"cute_modal_{title.lower().replace(' ', '_')}"
        self._inputs: list[TextInput] = []
        self._submit_callback: Callable[..., Coroutine[Any, Any, Any]] | None = None

    # ------------------------------------------------------------------
    # Builder methods
    # ------------------------------------------------------------------

    def add(self, input: TextInput) -> "Modal":
        """Add a :class:`~cutecord.components.TextInput` field to the modal."""
        self._inputs.append(input)
        return self

    def on_submit(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
    ) -> "Modal":
        """Attach an async callback for when the user submits the modal."""
        self._submit_callback = coro
        return self

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> ui.Modal:
        """Return the underlying :class:`discord.ui.Modal` ready to pass to ``send_modal``."""
        callback = self._submit_callback

        class _BuiltModal(ui.Modal):
            def __init__(self_inner) -> None:
                super().__init__(title=self._title, custom_id=self._custom_id)
                for inp in self._inputs:
                    self_inner.add_item(inp.build())

            async def callback(self_inner, interaction: discord.Interaction) -> None:
                if callback is not None:
                    await callback(interaction, self_inner)

        return _BuiltModal()

    # ------------------------------------------------------------------
    # Class-based shortcut
    # ------------------------------------------------------------------

    @staticmethod
    def as_class(title: str, *, custom_id: str = "") -> type[ui.Modal]:
        """
        Return a base :class:`discord.ui.Modal` subclass pre-configured with *title*.

        Useful for the class-based pattern where you declare inputs as class variables.

        Example
        -------
            class MyModal(Modal.as_class("My Form", custom_id="myform")):
                name = TextInput("name", "Your name").build()

                async def callback(self, interaction):
                    await interaction.response.send_message(f"Hi {self.name.value}!")
        """
        _cid = custom_id or f"cute_modal_{title.lower().replace(' ', '_')}"

        class _BaseModal(ui.Modal):
            pass

        _BaseModal.__init_subclass__()
        # Set title and custom_id on the class
        _BaseModal.title = title  # type: ignore[attr-defined]
        # discord.py reads title from __init__ kwarg, so we override __init__
        original_init = _BaseModal.__init__

        def new_init(self, **kwargs: Any) -> None:
            kwargs.setdefault("title", title)
            kwargs.setdefault("custom_id", _cid)
            original_init(self, **kwargs)

        _BaseModal.__init__ = new_init  # type: ignore[method-assign]
        return _BaseModal

    def to_dict(self) -> dict[str, Any]:
        """Return a raw JSON-serialisable representation of the modal."""
        return {
            "title": self._title,
            "custom_id": self._custom_id,
            "components": [
                {
                    "type": 1,  # ActionRow
                    "components": [inp.to_component_dict()],
                }
                for inp in self._inputs
            ],
        }

    def __repr__(self) -> str:
        return f"Modal(title={self._title!r}, inputs={len(self._inputs)})"
