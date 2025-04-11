from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase


# See https://developers.google.com/youtube/v3/docs/playlistItems


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PlaylistItemResourceId:
    kind: str
    video_id: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PlaylistItemSnippet:
    published_at: str
    channel_id: str
    title: str
    description: str
    video_owner_channel_title: str | None = None
    video_owner_channel_id: str | None = None
    position: int | None = None
    resource_id: PlaylistItemResourceId | None = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PlaylistItemStatus:
    privacy_status: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PlaylistItem:
    id: str
    snippet: PlaylistItemSnippet
    status: PlaylistItemStatus | None = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class APIResponse:
    next_page_token: str | None = None
    prev_page_token: str | None = None
    items: list[PlaylistItem] | None = None
