"""
cutecord — cog loader example
------------------------------
Shows how to split your bot into multiple files using cogs.

Folder layout:
    cogs_bot.py        ← this file (your main bot)
    cogs/
    ├── fun.py         ← Fun cog (roll, coinflip, 8-ball…)
    ├── info.py        ← Info cog (serverinfo, userinfo, ping)
    └── moderation.py  ← Moderation cog (kick, ban, timeout)

Create a .env file with:
    DISCORD_TOKEN=your_token_here
"""

import discord
from cutecord import Bot, Embed, Cog


bot = Bot()


# You can still define commands directly on the bot alongside cogs:
@bot.slash_command(description="Show what CuteCord can do")
async def about(ctx: discord.ApplicationContext):
    embed = (
        Embed("✨ CuteCord Bot")
        .color("blurple")
        .description("A demo bot built with **CuteCord** — the cute discord.py wrapper.")
        .field("Commands",   "/roll  /ping  /serverinfo  /userinfo  /kick  /ban", inline=False)
        .field("Made with",  "[CuteCord](https://github.com)",                     inline=True)
        .field("Library",    "py-cord",                                            inline=True)
        .footer("CuteCord v0.1.0")
    )
    await ctx.respond(embed=embed.build())


# You can also define a one-off cog inline (no separate file needed):
class Admin(Cog):
    """Admin-only commands."""

    @discord.slash_command(description="Reload all cogs")
    @discord.default_permissions(administrator=True)
    async def reload(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        reloaded = await bot.reload_cogs("cogs/")
        await ctx.respond(
            f"✅ Reloaded **{len(reloaded)}** cog(s): {', '.join(r.split('.')[-1] for r in reloaded)}",
            ephemeral=True,
        )


async def setup_hook():
    """Called once before the bot starts. Load cogs here."""
    await bot.load_cogs("cogs/")     # loads fun.py, info.py, moderation.py
    await bot.add_cog(Admin(bot))    # inline cog


bot.setup_hook = setup_hook

bot.run()
