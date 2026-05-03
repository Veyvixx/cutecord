"""
cutecord — Paginator example
------------------------------
Split long content across pages with ⏮ ◀ ▶ ⏭ navigation buttons.
"""

import discord
from cutecord import Bot, Embed, Cog
from cutecord.paginator import Paginator

bot = Bot()


class PaginatorDemo(Cog):

    @discord.slash_command(description="Show a multi-page embed")
    async def rules(self, ctx):
        """A multi-page rules list."""
        pages = [
            Embed("📋 Rules — Page 1")
            .color("gold")
            .description("**1. Be respectful**\nTreat everyone with respect.")
            .field("Also", "No harassment, slurs, or hate speech.", inline=False),

            Embed("📋 Rules — Page 2")
            .color("gold")
            .description("**2. No spam**\nNo repeated messages or wall-of-text dumps.")
            .field("Also", "Don't flood channels with images or links.", inline=False),

            Embed("📋 Rules — Page 3")
            .color("gold")
            .description("**3. Stay on topic**\nUse the right channels for the right conversations.")
            .field("Also", "Gaming talk goes in #gaming, art in #art, etc.", inline=False),
        ]
        pager = Paginator(pages, loop=True, show_index=True)
        await pager.send(ctx)

    @discord.slash_command(description="List all server members with pagination")
    async def memberlist(self, ctx):
        """Auto-paginate a big list of strings."""
        members = sorted(str(m) for m in ctx.guild.members if not m.bot)
        pager = Paginator.from_lines(
            members,
            title="👥 Members",
            color="blurple",
            per_page=15,
        )
        await pager.send(ctx, ephemeral=True)

    @discord.slash_command(description="Search members by name")
    async def search(
        self,
        ctx,
        query: discord.Option(str, "Name to search for"),  # type: ignore[valid-type]
    ):
        results = [
            str(m) for m in ctx.guild.members
            if query.lower() in m.display_name.lower()
        ]
        if not results:
            await ctx.error(f"No members found matching **{query}**.")
            return

        pager = Paginator.from_lines(
            results,
            title=f"🔍 Results for '{query}'",
            color="teal",
            per_page=10,
        )
        await pager.send(ctx)


async def setup_hook():
    await bot.add_cog(PaginatorDemo(bot))

bot.setup_hook = setup_hook
bot.run()
