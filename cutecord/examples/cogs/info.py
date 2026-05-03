"""
Example cog: Server & user info commands.
"""

import discord
from cutecord import Cog, Embed


class Info(Cog):
    """Server and user information commands."""

    description = "Info commands"

    @discord.slash_command(description="Show info about this server")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = (
            ctx.embed("{server}", server=guild.name)
            .color("blurple")
            .description(f"ID: `{guild.id}`")
            .thumbnail(guild.icon.url if guild.icon else "")
            .field("Owner",    guild.owner.mention if guild.owner else "Unknown", inline=True)
            .field("Members",  str(guild.member_count),                           inline=True)
            .field("Channels", str(len(guild.channels)),                          inline=True)
            .field("Roles",    str(len(guild.roles)),                             inline=True)
            .field("Boosts",   str(guild.premium_subscription_count),             inline=True)
            .field("Created",  guild.created_at.strftime("%d %b %Y"),             inline=True)
            .footer("CuteCord • Server Info")
            .timestamp()
        )
        await ctx.respond(embed=embed.build(), files=embed.files)

    @discord.slash_command(description="Show info about a user")
    async def userinfo(
        self,
        ctx,
        member: discord.Option(discord.Member, "The user to look up", required=False),  # type: ignore[valid-type]
    ):
        target = member or ctx.author
        roles = [r.mention for r in target.roles if r.name != "@everyone"]
        embed = (
            ctx.embed("{name}", name=target.display_name)
            .color("purple")
            .thumbnail(target.display_avatar.url)
            .field("Username",  str(target),                                inline=True)
            .field("ID",        f"`{target.id}`",                           inline=True)
            .field("Bot",       "Yes" if target.bot else "No",              inline=True)
            .field("Joined server",  target.joined_at.strftime("%d %b %Y") if target.joined_at else "?", inline=True)
            .field("Account created", target.created_at.strftime("%d %b %Y"),  inline=True)
            .field(f"Roles ({len(roles)})", " ".join(roles) or "None", inline=False)
            .footer("CuteCord • User Info")
            .timestamp()
        )
        await ctx.respond(embed=embed.build(), files=embed.files)

    @discord.slash_command(description="Show the bot's latency")
    async def ping(self, ctx):
        ms = round(self.bot.latency * 1000)
        color = "green" if ms < 100 else "yellow" if ms < 200 else "red"
        await ctx.info(f"Latency: **{ms}ms**", title="🏓 Pong!")
