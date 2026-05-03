"""
CuteCord — a cute, design-first wrapper around discord.py.

Quick start:
    from cutecord import Bot, Embed, Cog
    from cutecord.components import Button, Select, Modal, TextInput
    from cutecord.components import Container, Section, MediaGallery, Separator, Header
    from cutecord.checks import is_admin, has_role
    from cutecord.cooldowns import cooldown
    from cutecord.paginator import Paginator

    bot = Bot()  # auto-loads .env

    bot.set_log_channel(LOG_CHANNEL_ID)  # auto-log all events

    @bot.on_join
    async def welcome(member):
        await member.send(f"Welcome to the server, {member.mention}!")

    @bot.slash_command()
    @is_admin()
    @cooldown(10)
    async def hello(ctx):
        embed = (
            Embed("Hello, {name}!", name=ctx.author.name)
            .color("blurple")
            .description("Welcome to **{server}**!", server=ctx.guild.name)
            .field("Members", str(ctx.guild.member_count))
            .footer("Powered by CuteCord")
            .timestamp()
        )
        await ctx.respond(embed=embed.build(), files=embed.files)

    bot.load_cogs("cogs/")
    bot.run()
"""

from .bot import Bot
from .embed import Embed
from .cogs import Cog
from .context import CuteContext
from .templates import Template, load_template
from .utils import read_file, read_file_async
from .paginator import Paginator
from .checks import is_admin, is_mod, is_owner, has_role, in_channel, in_guild, bot_has_perms
from .cooldowns import cooldown, once_per, slow

from .components import (
    Button,
    ButtonStyle,
    Select,
    UserSelect,
    RoleSelect,
    MentionableSelect,
    ChannelSelect,
    TextInput,
    TextInputStyle,
    Modal,
    ActionRow,
    Container,
    Section,
    TextDisplay,
    Thumbnail,
    MediaGallery,
    MediaGalleryItem,
    FileComponent,
    Separator,
    SeparatorSpacing,
    Header,
    HeadingLevel,
)

__all__ = [
    # Core
    "Bot",
    "Embed",
    "Cog",
    "CuteContext",
    # Templates
    "Template",
    "load_template",
    # Files
    "read_file",
    "read_file_async",
    # Paginator
    "Paginator",
    # Checks
    "is_admin",
    "is_mod",
    "is_owner",
    "has_role",
    "in_channel",
    "in_guild",
    "bot_has_perms",
    # Cooldowns
    "cooldown",
    "once_per",
    "slow",
    # Components
    "Button",
    "ButtonStyle",
    "Select",
    "UserSelect",
    "RoleSelect",
    "MentionableSelect",
    "ChannelSelect",
    "TextInput",
    "TextInputStyle",
    "Modal",
    "ActionRow",
    "Container",
    "Section",
    "TextDisplay",
    "Thumbnail",
    "MediaGallery",
    "MediaGalleryItem",
    "FileComponent",
    "Separator",
    "SeparatorSpacing",
    "Header",
    "HeadingLevel",
]

__version__ = "0.1.0"
