from typing import Optional, List
import discord

class ErrorResponse:
    __slots__ = ("title", "description", "color")

    def __init__(self, title: str, description: str, color: int = 0xE74C3C):
        self.title = title
        self.description = description
        self.color = color

    def to_embed(self) -> discord.Embed:
        return discord.Embed(
            title=self.title,
            description=self.description,
            color=self.color
        )


ERROR_MAP: List[tuple] = [
    (["requires login", "login required", "this video requires login"], ErrorResponse(
        "YouTube Restriction",
        "I found the video, but YouTube is preventing playback.\n\n"
        "This is a YouTube restriction rather than a bot error.\n\n"
        "Things that often work:\n"
        "\u2022 Another upload of the same song\n"
        "\u2022 SoundCloud\n"
        "\u2022 Bandcamp\n"
        "\u2022 Direct audio links"
    )),
    (["must find sig function", "signature", "cipher"], ErrorResponse(
        "Encryption Changed",
        "YouTube changed their playback encryption.\n\n"
        "This video can't currently be streamed."
    )),
    (["video player configuration"], ErrorResponse(
        "YouTube Error",
        "YouTube returned a player configuration error.\n\n"
        "This usually means YouTube changed something on their end "
        "or the video format is not supported."
    )),
    (["all clients failed"], ErrorResponse(
        "Playback Failure",
        "All available YouTube clients failed to load this video.\n\n"
        "This is a known limitation with the current YouTube plugin. "
        "Try a different source or another upload of the same song."
    )),
    (["video unavailable", "this video is unavailable"], ErrorResponse(
        "Video Unavailable",
        "This video is unavailable. It may be private, deleted, "
        "or region-restricted."
    )),
    (["400", "status code 400", "bad request"], ErrorResponse(
        "Playback Error",
        "YouTube returned an error for this video.\n\n"
        "This is usually a temporary restriction. "
        "Try again later or use a different source."
    )),
    (["403", "status code 403", "forbidden"], ErrorResponse(
        "Access Denied",
        "YouTube has denied access to this video.\n\n"
        "It may be age-restricted, geo-blocked, or otherwise blocked."
    )),
]

FALLBACK_MAP: List[tuple] = [
    (["FAULT"], ErrorResponse(
        "Track Load Failed",
        "Something went wrong while looking up the track.\n\n"
        "This is a known limitation with YouTube playback. "
        "Try a different source like SoundCloud or Bandcamp."
    )),
    (["SUSPICIOUS"], ErrorResponse(
        "Track Load Failed",
        "The track could not be loaded due to a suspicious error."
    )),
]


def _find_match(text: str, patterns: List[str]) -> bool:
    lower = text.lower()
    return any(p.lower() in lower for p in patterns)


def map_error(data: dict) -> Optional[discord.Embed]:
    message = data.get("message", "") or ""
    cause = data.get("cause", "") or ""
    severity = data.get("severity", "") or ""
    combined = f"{message} {cause} {severity}"

    for patterns, response in ERROR_MAP:
        if _find_match(combined, patterns):
            return response.to_embed()

    for patterns, response in FALLBACK_MAP:
        if _find_match(severity, patterns):
            return response.to_embed()

    return None
