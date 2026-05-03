"""
cutecord — events + log channel example
-----------------------------------------
Shows every event decorator and how to configure the auto-log channel.
"""

import discord
from cutecord import Bot

bot = Bot()

# ── Auto-log EVERYTHING to one channel ──────────────────────────────────────
# Just call this with your log channel's ID before bot.run().
# Remove the '#' below and set the right channel ID.

# bot.set_log_channel(1234567890)

# Or pick specific events:
# bot.set_log_channel(1234567890, events=["join", "leave", "ban", "delete"])


# ── Custom event callbacks (run your own code too) ───────────────────────────

@bot.on_join
async def greet_member(member: discord.Member):
    """DM new members a welcome message."""
    try:
        await member.send(
            f"👋 Hey **{member.display_name}**, welcome to **{member.guild.name}**!\n"
            "Check out the rules channel before chatting."
        )
    except discord.Forbidden:
        pass  # Member has DMs disabled


@bot.on_leave
async def log_leave(member: discord.Member):
    """Print a console message when someone leaves."""
    print(f"[leave] {member} left {member.guild.name}")


@bot.on_ban
async def on_banned(guild: discord.Guild, user: discord.User):
    print(f"[ban] {user} was banned from {guild.name}")


@bot.on_unban
async def on_unbanned(guild: discord.Guild, user: discord.User):
    print(f"[unban] {user} was unbanned from {guild.name}")


@bot.on_nick_change
async def nick_changed(member: discord.Member, before: str, after: str):
    print(f"[nick] {member}: {before!r} → {after!r}")


@bot.on_role_add
async def role_added(member: discord.Member, role: discord.Role):
    print(f"[role+] {member} got {role.name}")


@bot.on_role_remove
async def role_removed(member: discord.Member, role: discord.Role):
    print(f"[role-] {member} lost {role.name}")


@bot.on_delete
async def message_deleted(message: discord.Message):
    print(f"[delete] {message.author}: {message.content[:50]!r}")


@bot.on_edit
async def message_edited(before: discord.Message, after: discord.Message):
    print(f"[edit] {after.author}: {before.content[:30]!r} → {after.content[:30]!r}")


@bot.on_boost
async def boosted(member: discord.Member):
    # Thank the booster in a specific channel, for example:
    # channel = bot.get_channel(BOOST_CHANNEL_ID)
    # await channel.send(f"💎 Thank you {member.mention} for boosting!")
    print(f"[boost] {member} boosted {member.guild.name}!")


@bot.on_unboost
async def unboosted(member: discord.Member):
    print(f"[unboost] {member} removed their boost from {member.guild.name}")


@bot.on_voice_join
async def voice_joined(member: discord.Member, channel: discord.VoiceChannel):
    print(f"[voice+] {member} joined #{channel.name}")


@bot.on_voice_leave
async def voice_left(member: discord.Member, channel: discord.VoiceChannel):
    print(f"[voice-] {member} left #{channel.name}")


@bot.on_voice_move
async def voice_moved(member: discord.Member, before: discord.VoiceChannel, after: discord.VoiceChannel):
    print(f"[voice→] {member}: #{before.name} → #{after.name}")


@bot.on_role_create
async def role_created(role: discord.Role):
    print(f"[role_create] New role: {role.name}")


@bot.on_role_delete
async def role_deleted(role: discord.Role):
    print(f"[role_delete] Deleted role: {role.name}")


@bot.on_channel_create
async def channel_created(channel: discord.abc.GuildChannel):
    print(f"[channel_create] #{channel.name}")


@bot.on_channel_delete
async def channel_deleted(channel: discord.abc.GuildChannel):
    print(f"[channel_delete] #{channel.name}")


bot.run()
