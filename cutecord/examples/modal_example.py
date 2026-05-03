"""
cutecord — modal example
------------------------
Shows how to build a popup form with TextInputs using the fluent API.
"""

import discord
from cutecord import Bot
from cutecord.components import (
    ActionRow,
    Button,
    Modal,
    TextInput,
)

bot = Bot()


@bot.slash_command(description="Open a feedback form")
async def feedback(ctx):
    modal = (
        Modal("Share your feedback", custom_id="feedback_form")
        .add(
            TextInput("subject", "Subject")
            .placeholder("What's this about?")
            .max_length(100)
        )
        .add(
            TextInput("body", "Your message", style="paragraph")
            .placeholder("Tell us everything…")
            .min_length(10)
            .max_length(1000)
        )
        .add(
            TextInput("email", "Email (optional)", style="short")
            .placeholder("you@example.com")
            .required(False)
            .max_length(100)
        )
        .on_submit(handle_feedback)
    )
    await ctx.send_modal(modal.build())


async def handle_feedback(interaction: discord.Interaction, form) -> None:
    subject = form.children[0].value
    body    = form.children[1].value
    email   = form.children[2].value or "not provided"

    await interaction.response.send_message(
        f"Thanks! Got your message about **{subject}** (email: {email}).",
        ephemeral=True,
    )
    # In a real bot you'd also log / DM / store this
    print(f"[feedback] {subject!r} | {email}\n{body}")


bot.run()
