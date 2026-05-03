"""
cutecord — Components v2 example
----------------------------------
Shows Container, Section, Thumbnail, Header, Separator, MediaGallery,
and FileComponent.  These require sending the raw payload via an HTTP
client (aiohttp / httpx) with the IS_COMPONENTS_V2 flag, or a library
that exposes the flag directly.

This example shows building the payload — integration with your HTTP
client is up to you.
"""

import json
from cutecord.components import (
    Container,
    Section,
    TextDisplay,
    Thumbnail,
    MediaGallery,
    MediaGalleryItem,
    Separator,
    Header,
    HeadingLevel,
    SeparatorSpacing,
    FileComponent,
)


def build_profile_card(username: str, avatar_url: str, bio: str, score: int) -> dict:
    """
    Build a rich profile card using Components v2.
    Returns a dict ready to POST to Discord's REST API.
    """
    card = (
        Container(color="blurple")
        .add(Header(f"{username}'s Profile", level=HeadingLevel.One))
        .add(Separator())
        .add(
            Section()
            .content(
                TextDisplay(f"**Bio:** {bio}"),
                TextDisplay(f"**Score:** {score} points"),
            )
            .accessory(Thumbnail(avatar_url, description=f"{username}'s avatar"))
        )
        .add(Separator(spacing="large", divider=False))
        .add(
            MediaGallery()
            .item(MediaGalleryItem("https://picsum.photos/seed/a/400/200", description="Achievement 1"))
            .item(MediaGalleryItem("https://picsum.photos/seed/b/400/200", description="Achievement 2"))
        )
    )

    return card.to_message_payload()


if __name__ == "__main__":
    payload = build_profile_card(
        username="Alice",
        avatar_url="https://cdn.discordapp.com/embed/avatars/0.png",
        bio="Discord bot enthusiast and Python lover.",
        score=9001,
    )
    print(json.dumps(payload, indent=2))
