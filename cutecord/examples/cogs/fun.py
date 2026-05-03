"""
Example cog: Fun commands.
Drop this in your cogs/ folder — bot.load_cogs("cogs/") picks it up automatically.
"""

import random
import discord
from cutecord import Cog, Embed


class Fun(Cog):
    """Fun and games commands."""

    description = "Fun commands"

    @discord.slash_command(description="Roll a dice (1–6 by default)")
    async def roll(
        self,
        ctx,
        sides: discord.Option(int, "Number of sides", default=6, min_value=2, max_value=100),  # type: ignore[valid-type]
    ):
        result = random.randint(1, sides)
        await ctx.info(
            "You rolled a **{result}** (d{sides})!",
            title="🎲 Dice Roll",
            result=result,
            sides=sides,
        )

    @discord.slash_command(description="Flip a coin")
    async def coinflip(self, ctx):
        side = random.choice(["Heads 🪙", "Tails 🪙"])
        await ctx.info(f"**{side}!**", title="Coin Flip")

    @discord.slash_command(description="Pick a random number between two values")
    async def random(
        self,
        ctx,
        low: discord.Option(int, "Minimum value", default=1),   # type: ignore[valid-type]
        high: discord.Option(int, "Maximum value", default=100),  # type: ignore[valid-type]
    ):
        if low >= high:
            await ctx.error("Minimum must be less than maximum.", ephemeral=True)
            return
        result = random.randint(low, high)
        await ctx.info(
            "**{result}**  *(between {low} and {high})*",
            title="🔢 Random Number",
            result=result, low=low, high=high,
        )

    @discord.slash_command(description="Ask the magic 8-ball a question")
    async def eightball(
        self,
        ctx,
        question: discord.Option(str, "Your question"),  # type: ignore[valid-type]
    ):
        answers = [
            "It is certain.", "Without a doubt.", "You may rely on it.",
            "Yes, definitely.", "As I see it, yes.", "Most likely.",
            "Reply hazy, try again.", "Ask again later.", "Cannot predict now.",
            "Don't count on it.", "My reply is no.", "Very doubtful.",
        ]
        embed = (
            ctx.embed("🎱 Magic 8-Ball")
            .color("dark")
            .field("Question", question)
            .field("Answer", random.choice(answers))
        )
        await ctx.respond(embed=embed.build())
