"""
Example cog: Basic moderation commands.
Shows how to use permissions and confirmation buttons inside a cog.
"""

import discord
from cutecord import Cog, Embed
from cutecord.components import ActionRow, Button


class Moderation(Cog):
    """Moderation commands."""

    description = "Moderation commands"

    @discord.slash_command(description="Kick a member from the server")
    @discord.default_permissions(kick_members=True)
    async def kick(
        self,
        ctx,
        member: discord.Option(discord.Member, "Member to kick"),  # type: ignore[valid-type]
        reason: discord.Option(str, "Reason", default="No reason provided"),  # type: ignore[valid-type]
    ):
        if member == ctx.author:
            await ctx.error("You can't kick yourself.")
            return

        async def do_kick(interaction: discord.Interaction):
            await member.kick(reason=f"{ctx.author}: {reason}")
            done = (
                Embed("✅ Member Kicked")
                .color("green")
                .description("**{member}** has been kicked.", member=str(member))
                .field("Reason", reason)
                .footer(f"Kicked by {ctx.author}", icon=ctx.author.display_avatar.url)
                .timestamp()
            )
            await interaction.response.edit_message(embed=done.build(), view=None)

        async def cancel(interaction: discord.Interaction):
            await interaction.response.edit_message(
                content="Kick cancelled.", embed=None, view=None
            )

        await ctx.confirm(
            "Are you sure you want to kick **{member}**?\n**Reason:** {reason}",
            title="⚠️ Confirm Kick",
            member=str(member),
            reason=reason,
            yes_label="Yes, kick",
            yes_style="danger",
            on_yes=do_kick,
            on_no=cancel,
        )

    @discord.slash_command(description="Ban a member from the server")
    @discord.default_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        member: discord.Option(discord.Member, "Member to ban"),  # type: ignore[valid-type]
        reason: discord.Option(str, "Reason", default="No reason provided"),  # type: ignore[valid-type]
        delete_days: discord.Option(int, "Days of messages to delete (0–7)", default=0, min_value=0, max_value=7),  # type: ignore[valid-type]
    ):
        if member == ctx.author:
            await ctx.error("You can't ban yourself.")
            return

        await member.ban(reason=f"{ctx.author}: {reason}", delete_message_days=delete_days)
        embed = (
            ctx.embed("🔨 Member Banned")
            .color("red")
            .description("**{member}** has been banned.", member=str(member))
            .field("Reason",           reason,               inline=True)
            .field("Messages Deleted", f"{delete_days}d",    inline=True)
            .footer(f"Banned by {ctx.author}", icon=ctx.author.display_avatar.url)
            .timestamp()
        )
        await ctx.respond(embed=embed.build())

    @discord.slash_command(description="Timeout (mute) a member")
    @discord.default_permissions(moderate_members=True)
    async def timeout(
        self,
        ctx,
        member: discord.Option(discord.Member, "Member to timeout"),  # type: ignore[valid-type]
        minutes: discord.Option(int, "Duration in minutes", default=10, min_value=1, max_value=10080),  # type: ignore[valid-type]
        reason: discord.Option(str, "Reason", default="No reason provided"),  # type: ignore[valid-type]
    ):
        import datetime
        duration = datetime.timedelta(minutes=minutes)
        await member.timeout_for(duration, reason=f"{ctx.author}: {reason}")
        await ctx.success(
            "**{member}** has been timed out for **{minutes}m**.\n**Reason:** {reason}",
            title="🔇 Member Timed Out",
            member=str(member), minutes=minutes, reason=reason,
        )
