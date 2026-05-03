"""
cutecord — file & attachment helpers example
---------------------------------------------
Shows read_file, read_file_async, attach, and attach_many.
"""

from cutecord import Bot, read_file, read_file_async
from cutecord.utils import attach, attach_many

bot = Bot()


@bot.slash_command(description="Show the server rules from a local file")
async def rules(ctx):
    text = read_file("content/rules.md")
    await ctx.respond(text[:2000])


@bot.slash_command(description="Send a log file as an attachment")
async def send_log(ctx):
    await ctx.respond(
        "Here's the latest log:",
        file=attach("logs/latest.log"),
    )


@bot.slash_command(description="Send multiple images at once")
async def gallery(ctx):
    await ctx.respond(
        "Check these out!",
        files=attach_many(
            "images/banner.png",
            "images/logo.png",
        ),
    )


@bot.slash_command(description="Read a file asynchronously")
async def async_read(ctx):
    text = await read_file_async("content/welcome.md")
    await ctx.respond(text[:2000])


bot.run()
