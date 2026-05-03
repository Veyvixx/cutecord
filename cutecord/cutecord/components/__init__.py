"""
CuteCord Components — all Discord UI components with a clean, fluent API.

Components
----------
Layout / containers (Discord "components v2"):
    Container       — coloured wrapper grouping multiple components
    Section         — side-by-side text + accessory layout
    TextDisplay     — rich-text block
    Thumbnail       — small image accessory (used inside Section)
    MediaGallery    — 1–10 image/video grid
    MediaGalleryItem — single item inside a MediaGallery
    FileComponent   — uploaded file attachment display
    Separator       — divider line with optional spacing
    Header          — large heading text (H1–H3)

Interactive:
    ActionRow       — container for up to 5 interactive components
    Button          — clickable button (ButtonStyle shortcuts included)
    Select          — string dropdown
    UserSelect      — user picker
    RoleSelect      — role picker
    MentionableSelect — user+role picker
    ChannelSelect   — channel picker
    TextInput       — single/multi-line text field (inside Modals)
    Modal           — popup form containing TextInputs

Enums / constants:
    ButtonStyle     — Primary, Secondary, Success, Danger, Link
    TextInputStyle  — Short, Paragraph
    SeparatorSpacing — Small, Large
    HeadingLevel    — One, Two, Three (H1/H2/H3)
"""

from .button import Button, ButtonStyle
from .select import Select, UserSelect, RoleSelect, MentionableSelect, ChannelSelect
from .text_input import TextInput, TextInputStyle
from .modal import Modal
from .action_row import ActionRow
from .containers import (
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
