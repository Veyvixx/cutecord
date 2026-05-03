"""
cutecord — template example
----------------------------
Load embed blueprints from JSON files and fill in variables at runtime.
"""

from cutecord import Bot, load_template, Template

bot = Bot()

# Reusable template object (loads file once, renders many times)
welcome_tmpl = Template("embeds/welcome.json")


@bot.slash_command(description="Send the welcome embed")
async def welcome(ctx):
    embed = welcome_tmpl.render(
        name=ctx.author.display_name,
        server=ctx.guild.name,
        count=ctx.guild.member_count,
    )
    await ctx.respond(embed=embed.build(), files=embed.files)


@bot.slash_command(description="Send a one-off embed from a file")
async def rules(ctx):
    embed = load_template(
        "embeds/rules.json",
        server=ctx.guild.name,
    )
    await ctx.respond(embed=embed.build())


bot.run()
