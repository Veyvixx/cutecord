"""
CuteCord Templates — load embed/message blueprints from JSON or YAML files,
fill in variables, and get a ready-to-send Embed back.

Supported formats
-----------------
  .json   — standard JSON
  .yaml / .yml — requires PyYAML (optional dep)

Template JSON schema
--------------------
    {
        "title": "Hello, {name}!",
        "description": "Welcome to **{server}**.",
        "color": "blurple",
        "thumbnail": "https://example.com/thumb.png",
        "image": "https://example.com/banner.png",
        "footer": { "text": "Sent by {bot}", "icon": "" },
        "author":  { "name": "{author}", "url": "", "icon": "" },
        "timestamp": true,
        "fields": [
            { "name": "Score", "value": "{score}/100", "inline": true }
        ]
    }

Usage
-----
    from cutecord import load_template, Template

    # One-shot: load file + fill variables + return Embed
    embed = load_template("embeds/welcome.json", name="Alice", server="My Server")

    # Reusable: keep a Template object and render many times
    tmpl = Template("embeds/welcome.json")
    embed1 = tmpl.render(name="Alice", server="My Server")
    embed2 = tmpl.render(name="Bob",   server="My Server")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .embed import Embed


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_raw(path: str | Path) -> dict[str, Any]:
    """Load a JSON or YAML file into a dict."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Template file not found: {p}")

    suffix = p.suffix.lower()
    if suffix in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML templates.  "
                "Install it with: pip install pyyaml"
            )
        with p.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    if suffix == ".json":
        with p.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    raise ValueError(f"Unsupported template format: {suffix!r} (use .json or .yaml)")


def _build_from_dict(data: dict[str, Any], **kwargs: Any) -> Embed:
    """Construct an Embed from a template dict + variable values."""
    embed = Embed(data.get("title", ""), **kwargs)

    if "color" in data:
        embed.color(data["color"])

    if "description" in data:
        embed.description(data["description"], **kwargs)

    if "url" in data:
        embed.url(data["url"])

    if data.get("timestamp"):
        embed.timestamp()

    if "thumbnail" in data:
        val = data["thumbnail"]
        if isinstance(val, str):
            embed.thumbnail(val)
        elif isinstance(val, dict):
            embed.thumbnail(
                url=val.get("url", ""),
                from_file=val.get("file") or None,
            )

    if "image" in data:
        val = data["image"]
        if isinstance(val, str):
            embed.image(val)
        elif isinstance(val, dict):
            embed.image(
                url=val.get("url", ""),
                from_file=val.get("file") or None,
            )

    if "author" in data:
        a = data["author"]
        if isinstance(a, str):
            embed.author(a, **kwargs)
        else:
            embed.author(
                a.get("name", ""),
                url=a.get("url", ""),
                icon=a.get("icon", ""),
                **kwargs,
            )

    if "footer" in data:
        f = data["footer"]
        if isinstance(f, str):
            embed.footer(f, **kwargs)
        else:
            embed.footer(
                f.get("text", ""),
                icon=f.get("icon", ""),
                **kwargs,
            )

    for field in data.get("fields", []):
        embed.field(
            field.get("name", "\u200b"),
            field.get("value", "\u200b"),
            inline=field.get("inline", False),
            **kwargs,
        )

    return embed


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class Template:
    """
    A reusable embed template loaded from a JSON or YAML file.

    Parameters
    ----------
    path:
        Path to the template file.

    Example
    -------
        tmpl = Template("embeds/welcome.json")
        embed = tmpl.render(name="Alice", server="My Server")
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._data: dict[str, Any] = _load_raw(self._path)

    def reload(self) -> None:
        """Re-read the template file from disk (useful in development)."""
        self._data = _load_raw(self._path)

    def render(self, **kwargs: Any) -> Embed:
        """
        Render the template with the given variable values.

        Returns a :class:`~cutecord.Embed` ready to be sent.
        """
        return _build_from_dict(self._data, **kwargs)

    def to_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return the rendered embed as a raw dict."""
        return self.render(**kwargs).to_dict()

    def __repr__(self) -> str:
        return f"Template({self._path!r})"


def load_template(path: str | Path, **kwargs: Any) -> Embed:
    """
    One-shot helper: load *path*, fill variables, return an :class:`~cutecord.Embed`.

    Parameters
    ----------
    path:
        JSON or YAML template file.
    **kwargs:
        Variable values substituted into every ``{placeholder}`` in the template.

    Example
    -------
        embed = load_template("embeds/welcome.json", name="Alice", score=99)
        await ctx.respond(embed=embed)
    """
    return _build_from_dict(_load_raw(path), **kwargs)
