"""
cutecord — CuteContext example
--------------------------------
Shows every ctx shortcut: success, error, info, warn, confirm, prompt, thinking.
"""

import discord
from cutecord import Bot, Cog, TextInput

bot = Bot()


class ContextDemo(Cog):

    # ── success ─────────────────────────────────────────────────────────
    @discord.slash_command(description="Give someone a gold star")
    async def give_star(
        self,
        ctx,
        member: discord.Option(discord.Member, "Who gets the star?"),  # type: ignore[valid-type]
    ):
        await ctx.success(
            "⭐ **{member}** just got a gold star!",
            member=member.display_name,
        )

    # ── error ────────────────────────────────────────────────────────────
    @discord.slash_command(description="Try something you don't have access to")
    async def restricted(self, ctx):
        await ctx.error("You don't have permission to do that.", ephemeral=True)

    # ── info ─────────────────────────────────────────────────────────────
    @discord.slash_command(description="Show server member count")
    async def members(self, ctx):
        await ctx.info(
            "This server has **{count}** members.",
            title="ℹ️ Member Count",
            count=ctx.guild.member_count,
        )

    # ── warn ─────────────────────────────────────────────────────────────
    @discord.slash_command(description="Warn the user about something")
    async def heads_up(self, ctx):
        await ctx.warn("This action cannot be undone. Proceed carefully.")

    # ── confirm ──────────────────────────────────────────────────────────
    @discord.slash_command(description="Delete a thing (with confirmation)")
    async def delete_thing(
        self,
        ctx,
        name: discord.Option(str, "What to delete"),  # type: ignore[valid-type]
    ):
        async def do_delete(interaction: discord.Interaction):
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=f"🗑️ **{name}** has been deleted.",
                    color=0x57F287,
                ),
                view=None,
            )

        async def cancelled(interaction: discord.Interaction):
            await interaction.response.edit_message(
                content="Cancelled.", embed=None, view=None
            )

        await ctx.confirm(
            "Are you sure you want to delete **{name}**?",
            name=name,
            yes_label="Delete it",
            yes_style="danger",
            on_yes=do_delete,
            on_no=cancelled,
        )

    # ── prompt (modal shortcut) ──────────────────────────────────────────
    @discord.slash_command(description="Change your nickname via a popup form")
    async def set_nick(self, ctx):
        async def handle(interaction: discord.Interaction, form):
            nick = form.children[0].value
            try:
                await interaction.user.edit(nick=nick)  # type: ignore[union-attr]
                await interaction.response.send_message(
                    f"✅ Nickname set to **{nick}**!", ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ I don't have permission to change your nickname.", ephemeral=True
                )

        await ctx.prompt(
            "Set Nickname",
            TextInput("nick", "New nickname").placeholder("Enter a nickname…").max_length(32),
            on_submit=handle,
        )

    # ── thinking ─────────────────────────────────────────────────────────
    @discord.slash_command(description="Simulate a slow operation")
    async def slow_command(self, ctx):
        await ctx.thinking()              # shows "Bot is thinking…"
        import asyncio
        await asyncio.sleep(3)            # pretend we're doing something slow
        await ctx.edit(content="✅ All done! That took a while.")


async def setup_hook():
    await bot.add_cog(ContextDemo(bot))

bot.setup_hook = setup_hook
bot.run()
