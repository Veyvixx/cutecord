# Cutecord

A cute, design-first Python wrapper around [discord.py / py-cord](https://docs.pycord.dev) that makes building beautiful Discord bots a joy.

**Why CuteCord?**
- 🎨 **Fluent embed builder** — chainable API, named colors, variable interpolation
- 🧩 **All Discord components** — buttons, selects, modals, and the full Components v2 set (Container, Section, MediaGallery, Header, Separator…)
- 🌍 **Built-in dotenv** — just create a `.env` file, CuteCord finds and loads it automatically
- 📄 **JSON/YAML templates** — store embed blueprints in files, fill variables at runtime
- 📁 **File helpers** — `read_file`, `attach`, `attach_many` — dead simple

---

## Installation

```bash
pip install cutecord
# or for development
pip install -e .
```

**Requirements:** Python 3.10+, py-cord 2.6+, python-dotenv, aiofiles

---

## Quick start

```python
from cutecord import Bot, Embed

bot = Bot()  # auto-loads .env and reads DISCORD_TOKEN

@bot.slash_command()
async def hello(ctx):
    embed = (
        Embed("Hey, {name}! 👋", name=ctx.author.display_name)
        .color("blurple")
        .description("Welcome to **{server}**!", server=ctx.guild.name)
        .field("Members", str(ctx.guild.member_count), inline=True)
        .footer("Powered by CuteCord")
        .timestamp()
    )
    await ctx.respond(embed=embed.build(), files=embed.files)

bot.run()
```

Create a `.env` file next to your script:

```env
DISCORD_TOKEN=your_token_here
```

---

## Embed builder

```python
from cutecord import Embed

embed = (
    Embed("Hello, {user}!", user="Alice")
    .color("blurple")            # named color
    .color("#ff6600")            # hex color
    .color(0x5865F2)             # int color
    .description("You joined **{server}**!", server="My Server")
    .url("https://discord.com")
    .thumbnail("https://example.com/avatar.png")
    .thumbnail(from_file="avatar.png")   # auto-attaches local file
    .image("https://example.com/banner.png")
    .image(from_file="banner.png")
    .author("CuteCord Bot", url="https://github.com", icon="logo.png")
    .footer("Sent by {bot}", icon="logo.png", bot="MyCuteBot")
    .field("Score", "{score}/100", inline=True, score=42)
    .blank_field()               # invisible spacer
    .timestamp()                 # current UTC time
)

# Send it
await ctx.respond(embed=embed.build(), files=embed.files)

# Or get the raw dict
print(embed.to_dict())
```

### Named colors

`blurple` · `fuchsia` · `green` · `yellow` · `red` · `white` · `dark` · `black` · `gold` · `orange` · `teal` · `purple` · `blue` · `navy` · `pink` · `cyan` · `lime` · `indigo` · `transparent`

---

## Variable interpolation

Every text field in `Embed`, `Template`, and `load_template` supports `{variable}` placeholders:

```python
embed = Embed("Hello, {name}!", name="Alice")
embed.description("You have {count} messages.", count=42)
embed.field("Status", "Your rank is **{rank}**", rank="Gold")
```

Missing variables are left as-is (no `KeyError`).

---

## JSON / YAML templates

Store embed designs in files, fill in variables at runtime.

**`embeds/welcome.json`:**
```json
{
    "title": "Welcome, {name}! 🎉",
    "color": "blurple",
    "description": "You've joined **{server}**!",
    "fields": [
        { "name": "Members", "value": "{count}", "inline": true }
    ],
    "footer": { "text": "Have fun!" },
    "timestamp": true
}
```

```python
from cutecord import load_template, Template

# One-shot
embed = load_template("embeds/welcome.json", name="Alice", server="My Server", count=500)
await ctx.respond(embed=embed.build())

# Reusable (load file once, render many times)
tmpl = Template("embeds/welcome.json")
embed = tmpl.render(name="Bob", server="My Server", count=501)
```

YAML is also supported — install `pyyaml` and use `.yaml` / `.yml` files.

---

## Components

### Buttons

```python
from cutecord.components import Button, ButtonStyle, ActionRow

# Style shortcuts
Button.primary("Confirm", custom_id="ok")
Button.danger("Delete",   custom_id="del")
Button.success("Done",    custom_id="done")
Button.secondary("Later", custom_id="later")
Button.link("Docs",       url="https://discord.com/developers")
Button.premium(sku_id="123456")

# Fluent style
btn = Button("Click me!", style="primary", custom_id="btn").emoji("🎉").disabled(False)

# Build an ActionRow and send
row = ActionRow().add(Button.primary("Yes", custom_id="y")).add(Button.danger("No", custom_id="n"))
await ctx.respond("Sure?", view=row.to_view())
```

### Select menus

```python
from cutecord.components import Select, UserSelect, RoleSelect, ChannelSelect

# String select (you define the options)
menu = (
    Select("colour_pick", placeholder="Pick a colour…")
    .option("Red",   "red",   emoji="🔴", description="Fiery red")
    .option("Blue",  "blue",  emoji="🔵", default=True)
    .min(1).max(1)
)

# Auto-populated selects
UserSelect("pick_user",    "Pick a user…").max(3)
RoleSelect("pick_role",    "Pick a role…")
ChannelSelect("pick_chan", "Pick a channel…")

# Send
row = ActionRow().add(menu)
await ctx.respond("Choose:", view=row.to_view())
```

### Modals

```python
from cutecord.components import Modal, TextInput

modal = (
    Modal("Feedback Form", custom_id="feedback")
    .add(TextInput("subject", "Subject").max_length(100))
    .add(TextInput("body", "Message", style="paragraph").min_length(10).max_length(1000))
    .add(TextInput("email", "Email (optional)").required(False))
    .on_submit(my_handler)
)
await ctx.send_modal(modal.build())

async def my_handler(interaction, form):
    subject = form.children[0].value
    await interaction.response.send_message(f"Got: {subject}", ephemeral=True)
```

---

## Components v2 (Container, Section, etc.)

Discord's newer layout system. Requires the `IS_COMPONENTS_V2` message flag.

```python
from cutecord.components import (
    Container, Section, TextDisplay, Thumbnail,
    MediaGallery, MediaGalleryItem, Separator,
    Header, HeadingLevel, FileComponent,
)

card = (
    Container(color="blurple")
    .add(Header("Welcome!", level=HeadingLevel.One))
    .add(Separator())
    .add(
        Section()
        .content(TextDisplay("Here is your profile."))
        .accessory(Thumbnail("https://example.com/avatar.png"))
    )
    .add(Separator(spacing="large", divider=False))
    .add(
        MediaGallery()
        .item(MediaGalleryItem("https://example.com/photo1.png", description="Photo 1"))
        .item(MediaGalleryItem("https://example.com/photo2.png"))
    )
)

# Get the raw API payload (pass to your HTTP client)
payload = card.to_message_payload()
```

---

## File helpers

```python
from cutecord import read_file, read_file_async
from cutecord.utils import attach, attach_many

# Read text files
text = read_file("content/rules.md")
text = await read_file_async("content/welcome.md")

# Send files as attachments
await ctx.respond("Log:", file=attach("logs/latest.log"))
await ctx.respond("Images:", files=attach_many("img1.png", "img2.png"))

# Use local files in embeds
embed = Embed("Gallery").image(from_file="banner.png")
await ctx.respond(embed=embed.build(), files=embed.files)
```

---

## Bot configuration

```python
bot = Bot(
    token_var="MY_TOKEN_VAR",   # env var name (default: DISCORD_TOKEN)
    dotenv_path=".env.prod",    # explicit .env path (default: auto-discover)
    log_level=logging.DEBUG,    # logging level (default: INFO)
    command_prefix="!",         # prefix for text commands
)

bot.run()          # reads DISCORD_TOKEN from .env
bot.run("TOKEN")   # pass token directly
```

---

## Events + auto log channel

Every guild event has a friendly decorator. No more `async def on_member_join` overrides.

```python
@bot.on_join
async def welcome(member):
    await member.send(f"Welcome, {member.mention}!")

@bot.on_ban
async def banned(guild, user):
    print(f"{user} was banned from {guild.name}")

@bot.on_delete
async def deleted(message):
    print(f"Deleted: {message.content}")

@bot.on_boost
async def boosted(member):
    await some_channel.send(f"💎 {member.mention} boosted!")
```

**All supported events:**

| Decorator | Callback args |
|---|---|
| `@bot.on_join` | `(member)` |
| `@bot.on_leave` | `(member)` |
| `@bot.on_ban` | `(guild, user)` |
| `@bot.on_unban` | `(guild, user)` |
| `@bot.on_nick_change` | `(member, before, after)` |
| `@bot.on_role_add` | `(member, role)` |
| `@bot.on_role_remove` | `(member, role)` |
| `@bot.on_delete` | `(message)` |
| `@bot.on_edit` | `(before, after)` |
| `@bot.on_role_create` | `(role)` |
| `@bot.on_role_delete` | `(role)` |
| `@bot.on_channel_create` | `(channel)` |
| `@bot.on_channel_delete` | `(channel)` |
| `@bot.on_boost` | `(member)` |
| `@bot.on_unboost` | `(member)` |
| `@bot.on_voice_join` | `(member, channel)` |
| `@bot.on_voice_leave` | `(member, channel)` |
| `@bot.on_voice_move` | `(member, before_ch, after_ch)` |

### Auto log channel

One line to send a styled embed for every event automatically:

```python
bot.set_log_channel(1234567890)                                  # log everything
bot.set_log_channel(1234567890, events=["join", "leave", "ban"]) # specific events
```

---

## Permission checks

```python
from cutecord.checks import is_admin, is_mod, is_owner, has_role, in_channel, bot_has_perms

@bot.slash_command()
@is_admin()
async def nuke(ctx): ...

@bot.slash_command()
@has_role("Moderator", "Admin")
async def warn(ctx): ...

@bot.slash_command()
@is_owner()
async def reload(ctx): ...

@bot.slash_command()
@in_channel(123456789)
async def daily(ctx): ...

@bot.slash_command()
@bot_has_perms(manage_messages=True)
async def purge(ctx): ...
```

Failed checks are caught by CuteCord's error handler and sent as a red embed automatically.

---

## Cooldowns

```python
from cutecord.cooldowns import cooldown, once_per, slow

@cooldown(10)               # once every 10s per user
@cooldown(30, per="guild")  # once every 30s per guild
@cooldown(60, rate=3)       # 3 times per 60s per user

@once_per(30)               # readable alias
@slow(5)                    # shorthand for cooldown(5)
```

Cooldown errors are caught by the error handler automatically.

---

## Error handling

CuteCord automatically catches all slash command errors and sends a red embed. No setup required.

### Map exceptions to messages

```python
bot.map_error(ValueError, "Invalid value: {error}")
bot.map_error(PermissionError, "You don't have permission.")
```

### Override the handler entirely

```python
@bot.on_command_error
async def my_handler(ctx, error):
    await ctx.error(str(error))
```

**Built-in errors handled automatically:**
- Missing permissions (user + bot)
- Command on cooldown
- Missing arguments
- Not owner, no private message, private message only
- `discord.Forbidden`, `discord.NotFound`

---

## Paginator

Split long content across multiple embed pages with ⏮ ◀ ▶ ⏭ buttons.

```python
from cutecord.paginator import Paginator

# Manual pages
pages = [
    Embed("Page 1").color("blurple").description("First"),
    Embed("Page 2").color("blurple").description("Second"),
    Embed("Page 3").color("blurple").description("Third"),
]
pager = Paginator(pages, loop=True, show_index=True)
await pager.send(ctx)

# Auto-paginate a list of strings
members = [str(m) for m in ctx.guild.members]
pager = Paginator.from_lines(members, title="Members", per_page=15)
await pager.send(ctx)
```

Only the command invoker can flip pages.

---

## Context shortcuts — one-liner responses

Every slash command `ctx` has built-in response helpers. No embed building needed.

```python
# ✅ Green success message
await ctx.success("Kicked **{member}**!", member=str(target))

# ❌ Red error (ephemeral by default)
await ctx.error("You don't have permission to do that.")

# ℹ️ Blurple info
await ctx.info("There are **{count}** members online.", count=42)

# ⚠️ Yellow warning
await ctx.warn("This action cannot be undone.")
```

All of them support `{variable}` placeholders and accept `ephemeral=True` / `delete_after=10`.

### Custom title

```python
await ctx.success("All files uploaded.", title="✅ Upload Complete")
await ctx.error("Invalid token.", title="❌ Auth Failed")
```

### Confirmation dialog

```python
await ctx.confirm(
    "Delete **{name}**?", name=item_name,
    yes_label="Delete it",
    yes_style="danger",
    on_yes=do_delete,       # async callback(interaction)
    on_no=send_cancelled,   # optional
    timeout=30,
)
```

### Modal shortcut

```python
await ctx.prompt(
    "Set Nickname",
    TextInput("nick", "New nickname").max_length(32),
    on_submit=handle_nick,  # async callback(interaction, form)
)
```

### Thinking indicator (for slow commands)

```python
await ctx.thinking()
result = await some_slow_api_call()
await ctx.edit(content=result)
```

### Use an Embed builder directly

```python
embed = ctx.embed("Profile — {name}", name=ctx.author.display_name)
embed.color("teal").field("Score", "100")
await ctx.respond(embed=embed.build())
```

---

## Cog loader — split your bot across files

No more giant `bot.py`. Put each feature in its own file, and CuteCord loads them all automatically.

```
your-bot/
├── .env
├── bot.py
└── cogs/
    ├── fun.py        ← class Fun(Cog): ...
    ├── info.py       ← class Info(Cog): ...
    └── moderation.py ← class Moderation(Cog): ...
```

**`bot.py`:**
```python
from cutecord import Bot

bot = Bot()

async def setup_hook():
    await bot.load_cogs("cogs/")  # loads fun, info, moderation automatically

bot.setup_hook = setup_hook
bot.run()
```

**`cogs/fun.py`:**
```python
import discord
from cutecord import Cog, Embed

class Fun(Cog):
    @discord.slash_command(description="Roll a dice")
    async def roll(self, ctx):
        import random
        embed = Embed("🎲 You rolled {n}!", n=random.randint(1, 6)).color("gold")
        await ctx.respond(embed=embed.build())
```

That's it — no `setup()` function needed. CuteCord writes it for you.

### Other cog methods

```python
# In an admin command, hot-reload all cogs without restarting the bot:
await bot.reload_cogs("cogs/")

# Unload all cogs from a folder:
await bot.unload_cogs("cogs/")
```

**Rules:**
- One class per file (the class name doesn't matter, just subclass `Cog`)
- Files starting with `_` are skipped (`__init__.py`, `_helpers.py`, etc.)
- You can still define commands directly on `bot` alongside cogs

---

## Project layout

```
your-bot/
├── .env                    ← DISCORD_TOKEN=...
├── bot.py                  ← your main bot file
├── embeds/
│   ├── welcome.json        ← embed templates
│   └── rules.json
├── content/
│   └── rules.md            ← text file content
└── images/
    └── banner.png
```
