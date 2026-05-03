"""
cutecord — error handler example
----------------------------------
CuteCord automatically handles all slash command errors and sends
a clean red embed. Here's how to customise it.
"""

import discord
from cutecord import Bot, Cog
from cutecord.checks import is_admin

bot = Bot()


# ── Option 1: Map specific exceptions to friendly messages ──────────────────
bot.map_error(ValueError,     "Invalid value: {error}")
bot.map_error(PermissionError, "You don't have permission to do that.")


# ── Option 2: Fully override the error handler ──────────────────────────────
# @bot.on_command_error
# async def my_handler(ctx, error):
#     cause = getattr(error, "original", error)
#     await ctx.error(f"Oops! {cause}")


class ErrorsDemo(Cog):

    @discord.slash_command(description="Trigger a ValueError (auto-handled)")
    async def bad_value(self, ctx):
        raise ValueError("this is not a valid input")

    @discord.slash_command(description="Admin-only (shows permission error)")
    @is_admin()
    async def secret(self, ctx):
        await ctx.success("Only admins can see this.")

    @discord.slash_command(description="Trigger an unhandled error (generic message)")
    async def crash(self, ctx):
        raise RuntimeError("Something exploded internally")


async def setup_hook():
    await bot.add_cog(ErrorsDemo(bot))

bot.setup_hook = setup_hook
bot.run()
