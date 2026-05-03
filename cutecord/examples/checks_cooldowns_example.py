"""
cutecord — checks + cooldowns example
---------------------------------------
Shows every permission check and cooldown decorator.
Errors are handled automatically by CuteCord's error handler.
"""

import discord
from cutecord import Bot, Cog
from cutecord.checks import is_admin, is_mod, is_owner, has_role, in_channel, bot_has_perms
from cutecord.cooldowns import cooldown, once_per, slow

bot = Bot()

# You can also map custom exceptions to friendly messages:
# bot.map_error(ValueError, "Invalid value provided: {error}")

# Or override the whole error handler:
# @bot.on_command_error
# async def my_handler(ctx, error):
#     await ctx.error(str(error))


class ChecksDemo(Cog):

    # ── Permission checks ─────────────────────────────────────────────────

    @discord.slash_command(description="Admin-only command")
    @is_admin()
    async def admin_cmd(self, ctx):
        await ctx.success("You're an admin!")

    @discord.slash_command(description="Mod-only command")
    @is_mod()
    async def mod_cmd(self, ctx):
        await ctx.success("You're a mod!")

    @discord.slash_command(description="Bot owner only")
    @is_owner()
    async def owner_cmd(self, ctx):
        await ctx.success("You're the bot owner!")

    @discord.slash_command(description="Only for members with 'VIP' or 'Supporter' role")
    @has_role("VIP", "Supporter")
    async def vip_cmd(self, ctx):
        await ctx.success("Welcome, VIP member!")

    # ── Cooldowns ────────────────────────────────────────────────────────

    @discord.slash_command(description="Can be used once every 10 seconds per user")
    @cooldown(10)
    async def basic_cooldown(self, ctx):
        await ctx.success("Used! Try again in 10 seconds.")

    @discord.slash_command(description="5 seconds cooldown — per channel")
    @cooldown(5, per="channel")
    async def channel_cooldown(self, ctx):
        await ctx.info("This channel is rate-limited to once every 5s.")

    @discord.slash_command(description="3 uses per 60 seconds per guild")
    @cooldown(60, rate=3, per="guild")
    async def guild_ratelimit(self, ctx):
        await ctx.info("This server can use this up to 3 times per minute.")

    @discord.slash_command(description="Once per 30 seconds — readable alias")
    @once_per(30)
    async def once_cmd(self, ctx):
        await ctx.success("You can use this once every 30 seconds.")

    @discord.slash_command(description="Slow command — 15s cooldown")
    @slow(15)
    async def slow_cmd(self, ctx):
        await ctx.info("Slow command — 15s cooldown per user.")

    # ── Combined ─────────────────────────────────────────────────────────

    @discord.slash_command(description="Admin, cooldown, and bot permissions all at once")
    @is_admin()
    @cooldown(60)
    @bot_has_perms(manage_messages=True)
    async def purge_hint(self, ctx):
        await ctx.success("All checks passed!")


async def setup_hook():
    await bot.add_cog(ChecksDemo(bot))

bot.setup_hook = setup_hook
bot.run()
