"""
cutecord — basic bot example
----------------------------
Create a .env file next to this script with:
    DISCORD_TOKEN=your_token_here
"""

from cutecord import Bot, Embed
from cutecord.components import (
    ActionRow,
    Button,
    Select,
)

bot = Bot()  # auto-loads .env, reads DISCORD_TOKEN


# ---------------------------------------------------------------------------
# /hello — basic embed with variables
# ---------------------------------------------------------------------------

@bot.slash_command(description="Say hello")
async def hello(ctx):
    embed = (
        Embed("Hey, {name}! 👋", name=ctx.author.display_name)
        .color("blurple")
        .description(
            "You're on **{server}** and there are **{count}** members here.",
            server=ctx.guild.name,
            count=ctx.guild.member_count,
        )
        .field("Your ID", str(ctx.author.id), inline=True)
        .field("Joined", ctx.author.joined_at.strftime("%d %b %Y") if ctx.author.joined_at else "Unknown", inline=True)
        .footer("Powered by CuteCord ✨")
        .timestamp()
    )
    await ctx.respond(embed=embed.build(), files=embed.files)


# ---------------------------------------------------------------------------
# /confirm — buttons
# ---------------------------------------------------------------------------

@bot.slash_command(description="Confirm / deny with buttons")
async def confirm(ctx):
    row = (
        ActionRow()
        .add(Button.success("Yes please!", custom_id="yes"))
        .add(Button.danger("Nope", custom_id="no"))
        .add(Button.link("Docs", url="https://docs.discord.com"))
    )
    await ctx.respond("Are you sure?", view=row.to_view())


# ---------------------------------------------------------------------------
# /pick — select menu
# ---------------------------------------------------------------------------

@bot.slash_command(description="Pick your favourite colour")
async def pick(ctx):
    menu = (
        Select("fav_colour", placeholder="Pick a colour…")
        .option("Blurple", "blurple", emoji="🟣", description="Discord's signature")
        .option("Red",     "red",     emoji="🔴")
        .option("Green",   "green",   emoji="🟢")
        .option("Gold",    "gold",    emoji="🟡")
        .min(1).max(1)
    )
    row = ActionRow().add(menu)
    await ctx.respond("What's your fav?", view=row.to_view())


bot.run()
